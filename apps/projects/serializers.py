from __future__ import annotations

from rest_framework import serializers
from .models import Project
from apps.workspaces.models import Workspace


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "workspace", "name", "slug", "description", "status", "created_at"]
        read_only_fields = ["id", "slug", "created_at"]

    def validate_workspace(self, value: Workspace) -> Workspace:
        request = self.context["request"]
        if not value.memberships.filter(user=request.user).exists():
            raise serializers.ValidationError("You do not have access to this workspace.")
        return value