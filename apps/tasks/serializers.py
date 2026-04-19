from __future__ import annotations

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.automation.tasks import notify_status_change

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Task, TaskHistory
from apps.projects.models import Project
from apps.workspaces.models import Membership, Workspace

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id", "project", "title", "description", "status",
            "priority", "assignee", "due_date", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_project(self, value: Project) -> Project:
        request = self.context["request"]
        if not value.workspace.memberships.filter(user=request.user).exists():
            raise serializers.ValidationError("You do not have access to this project's workspace.")
        return value

    def validate(self, attrs: dict) -> dict:
        request = self.context["request"]
        project = attrs.get("project") or (self.instance.project if self.instance else None)
        if project and attrs.get("assignee"):
            if not Membership.objects.filter(workspace=project.workspace, user=attrs["assignee"]).exists():
                raise serializers.ValidationError({"assignee": "User must be a member of this workspace."})
        return attrs

    def _broadcast(self, instance: Task, action: str) -> None:
        channel_layer = get_channel_layer()
        group = f"workspace_{instance.project.workspace_id}"
        async_to_sync(channel_layer.group_send)(
            group,
            {
                "type": "task.update",
                "payload": {
                    "action": action,
                    "task_id": str(instance.id),
                    "workspace_id": str(instance.project.workspace_id),
                    "project_id": str(instance.project_id),
                    "title": instance.title,
                    "status": instance.status,
                    "priority": instance.priority,
                    "assignee_id": str(instance.assignee_id) if instance.assignee else None,
                    "updated_at": instance.updated_at.isoformat(),
                },
            },
        )
        
    def update(self, instance: Task, validated_data: dict[str, any]) -> Task:
        tracked_changes = []
        for field in ("status", "assignee", "due_date"):
            if field in validated_data:
                old = getattr(instance, field)
                new = validated_data[field]
                if old != new:
                    tracked_changes.append({
                        "field": field,
                        "old": str(old) if old is not None else "",
                        "new": str(new) if new is not None else "",
                    })

        instance = super().update(instance, validated_data)
        actor = self.context["request"].user

        # Trigger async notification on status change
        for change in tracked_changes:
            if change["field"] == "status":
                notify_status_change.delay(
                    str(instance.id),
                    actor.id,
                    change["old"],
                    change["new"],
                )

        # Create audit records
        for change in tracked_changes:
            TaskHistory.objects.create(
                task=instance,
                actor=actor,
                change_type=f"{change['field']}_changed",
                old_value=change["old"],
                new_value=change["new"],
            )
        self._broadcast(instance, "updated")
        return instance

    def create(self, validated_data: dict[str, any]) -> Task:
        validated_data["reporter"] = self.context["request"].user
        instance = super().create(validated_data)
        self._broadcast(instance, "created")
        return instance
    


class TaskHistorySerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)

    class Meta:
        model = TaskHistory
        fields = ["id", "change_type", "old_value", "new_value", "actor_email", "created_at"]
        read_only_fields = fields