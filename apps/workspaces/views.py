from __future__ import annotations

from rest_framework import viewsets, permissions

from .models import Workspace
from .serializers import WorkspaceSerializer
from .permissions import HasWorkspaceRole, MembershipRole


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(
            memberships__user=self.request.user
        ).select_related("owner").order_by("-created_at")

    def perform_update(self, serializer: WorkspaceSerializer) -> None:
        # Only admins can modify workspace settings
        workspace = self.get_object()
        if workspace.memberships.get(user=self.request.user).role != MembershipRole.ADMIN:
            self.permission_denied(self.request, message="Only workspace admins can edit.")
        serializer.save()

    def perform_destroy(self, instance: Workspace) -> None:
        if instance.memberships.get(user=self.request.user).role != MembershipRole.ADMIN:
            self.permission_denied(self.request, message="Only workspace admins can delete.")
        instance.delete()