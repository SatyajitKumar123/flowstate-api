from __future__ import annotations

from rest_framework import viewsets, permissions
from .models import WebhookEndpoint
from .serializers import WebhookEndpointSerializer
from apps.workspaces.models import MembershipRole

class WebhookEndpointViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WebhookEndpoint.objects.filter(
            workspace__memberships__user=self.request.user
        ).select_related("workspace").order_by("-created_at")

    def perform_create(self, serializer: WebhookEndpointSerializer) -> None:
        serializer.save()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ("PUT", "PATCH", "DELETE"):
            membership = obj.workspace.memberships.filter(user=request.user).first()
            if not membership or membership.role != MembershipRole.ADMIN:
                self.permission_denied(request, "Only workspace admins can modify webhooks.")