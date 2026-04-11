from __future__ import annotations

from rest_framework import viewsets, permissions

from .models import Project
from .serializers import ProjectSerializer
from apps.workspaces.permissions import HasWorkspaceRole, MembershipRole


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, HasWorkspaceRole.with_role(MembershipRole.VIEWER)]

    def get_queryset(self):
        return Project.objects.filter(
            workspace__memberships__user=self.request.user
        ).select_related("workspace").order_by("-created_at")

    def perform_update(self, serializer: ProjectSerializer) -> None:
        # Members+ can edit, Viewers get blocked by permission class
        if not HasWorkspaceRole.with_role(MembershipRole.MEMBER).has_object_permission(
            self.request, self, self.get_object()
        ):
            self.permission_denied(self.request, message="Viewers cannot edit projects.")
        serializer.save()

    def perform_destroy(self, instance: Project) -> None:
        if not HasWorkspaceRole.with_role(MembershipRole.ADMIN).has_object_permission(
            self.request, self, instance
        ):
            self.permission_denied(self.request, message="Only workspace admins can delete projects.")
        instance.delete()