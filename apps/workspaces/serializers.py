from __future__ import annotations

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Workspace, Membership, MembershipRole

User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ["id", "name", "slug", "description", "is_active", "created_at", "role"]
        read_only_fields = ["id", "slug", "created_at", "role"]

    def get_role(self, obj: Workspace) -> str | None:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        membership = obj.memberships.filter(user=request.user).first()
        return membership.role if membership else None

    def create(self, validated_data: dict) -> Workspace:
        validated_data["owner"] = self.context["request"].user
        workspace = super().create(validated_data)
        Membership.objects.create(
            workspace=workspace,
            user=validated_data["owner"],
            role=MembershipRole.ADMIN,
        )
        return workspace