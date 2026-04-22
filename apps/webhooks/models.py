from __future__ import annotations

import uuid
import secrets
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.workspaces.models import Workspace

class WebhookEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="webhook_endpoints"
    )
    url = models.URLField(verbose_name=_("Endpoint URL"))
    secret = models.CharField(max_length=64, default=secrets.token_urlsafe, editable=False)
    event_types = models.JSONField(
        default=list,
        help_text=_("e.g. ['task.created', 'task.updated', 'task.deleted']")
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "webhook_endpoints"
        verbose_name = _("Webhook Endpoint")
        verbose_name_plural = _("Webhook Endpoints")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workspace", "is_active"])]

    def __str__(self) -> str:
        return f"{self.workspace.name} → {self.url}"


class WebhookDelivery(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="deliveries")
    event_type = models.CharField(max_length=30)
    payload = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    response_status = models.SmallIntegerField(null=True, blank=True)
    response_body = models.TextField(max_length=2000, blank=True, default="")
    attempt = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "webhook_deliveries"
        verbose_name = _("Webhook Delivery")
        verbose_name_plural = _("Webhook Deliveries")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["endpoint", "status"])]