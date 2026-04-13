from __future__ import annotations

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task, TaskHistory
from .serializers import TaskSerializer, TaskHistorySerializer
from apps.workspaces.models import MembershipRole


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Explicit tenant scoping: only tasks in workspaces the user belongs to
        return Task.objects.filter(
            project__workspace__memberships__user=self.request.user
        ).select_related(
            "project", "project__workspace", "assignee", "reporter"
        ).distinct().order_by("-created_at")

    def perform_create(self, serializer: TaskSerializer) -> None:
        # Only Admin & Member can create tasks
        workspace = serializer.validated_data["project"].workspace
        has_role = workspace.memberships.filter(
            user=self.request.user,
            role__in=[MembershipRole.ADMIN, MembershipRole.MEMBER]
        ).exists()
        if not has_role:
            self.permission_denied(self.request, message="Viewers cannot create tasks.")
        serializer.save()

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        task = self.get_object()
        history_qs = TaskHistory.objects.filter(task=task).select_related("actor").order_by("-created_at")
        return Response(TaskHistorySerializer(history_qs, many=True, context={"request": request}).data)