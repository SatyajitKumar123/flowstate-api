from __future__ import annotations

from rest_framework import permissions
from .models import Membership, MembershipRole


class HasWorkspaceRole(permissions.BasePermission):
    """
    Grants access if user holds at least the required role in the workspace.
    Usage: permission_classes = [HasWorkspaceRole.with_role(MembershipRole.MEMBER)]
    """
    required_role = MembershipRole.MEMBER

    @classmethod
    def with_role(cls, role: str) -> type["HasWorkspaceRole"]:
        return type(f"HasWorkspaceRole_{role}", (cls,), {"required_role": role})

    def has_object_permission(self, request: object, view: object, obj: object) -> bool:
        workspace = obj.workspace if hasattr(obj, "workspace") else obj
        return workspace.memberships.filter(
            user=request.user,
            role__in=self._role_hierarchy(self.required_role),
        ).exists()

    @staticmethod
    def _role_hierarchy(role: str) -> tuple[str, ...]:
        hierarchy = {
            MembershipRole.ADMIN: (MembershipRole.ADMIN, MembershipRole.MEMBER, MembershipRole.VIEWER),
            MembershipRole.MEMBER: (MembershipRole.MEMBER, MembershipRole.VIEWER),
            MembershipRole.VIEWER: (MembershipRole.VIEWER,),
        }
        return hierarchy.get(role, (MembershipRole.VIEWER,))