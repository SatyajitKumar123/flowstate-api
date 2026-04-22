from __future__ import annotations

import json
from datetime import datetime, timezone
from .models import WebhookEndpoint, WebhookDelivery
from .tasks import deliver_webhook

def dispatch_webhooks(event_type: str, workspace_slug: str, data: dict) -> None:
    """
    Finds active endpoints matching event_type, creates delivery records,
    and queues async delivery via Celery.
    """
    endpoints = WebhookEndpoint.objects.filter(
        workspace__slug=workspace_slug,
        is_active=True,
        event_types__contains=[event_type]
    )

    payload = json.dumps({
        "event": event_type,
        "workspace_slug": workspace_slug,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }, separators=(",", ":"))

    for endpoint in endpoints:
        delivery = WebhookDelivery.objects.create(
            endpoint=endpoint,
            event_type=event_type,
            payload=payload,
        )
        deliver_webhook.delay(str(delivery.id))