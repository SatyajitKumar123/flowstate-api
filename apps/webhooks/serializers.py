from __future__ import annotations

from rest_framework import serializers
from .models import WebhookEndpoint

class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ["id", "url", "secret", "event_types", "is_active", "created_at"]
        read_only_fields = ["id", "secret", "created_at"]

    def validate_event_types(self, value: list[str]) -> list[str]:
        allowed = {"task.created", "task.updated", "task.deleted", "status_changed"}
        invalid = set(value) - allowed
        if invalid:
            raise serializers.ValidationError(f"Unsupported events: {invalid}")
        return list(dict.fromkeys(value)) 