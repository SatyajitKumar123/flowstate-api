from __future__ import annotations

import hmac
import hashlib
import logging
import requests
from celery import shared_task

from .models import WebhookDelivery

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=4,
    retry_backoff=True,
    retry_backoff_max=300,
    acks_late=True,
    name="flowstate.deliver_webhook"
)
def deliver_webhook(self, delivery_id: str) -> None:
    try:
        delivery = WebhookDelivery.objects.select_related("endpoint").get(id=delivery_id)
    except WebhookDelivery.DoesNotExist:
        logger.warning("WebhookDelivery %s not found", delivery_id)
        return

    endpoint = delivery.endpoint
    payload_bytes = delivery.payload.encode()
    signature = hmac.new(
        endpoint.secret.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "FlowState-Webhook/1.0",
        "X-FlowState-Signature": f"sha256={signature}",
    }

    try:
        resp = requests.post(
            endpoint.url,
            data=payload_bytes,
            headers=headers,
            timeout=10,
            allow_redirects=False,
        )
        delivery.response_status = resp.status_code
        delivery.response_body = resp.text[:2000]
        delivery.status = "success" if 200 <= resp.status_code < 300 else "failed"
    except requests.RequestException as exc:
        logger.error("Webhook delivery failed for %s: %s", delivery_id, exc)
        delivery.status = "failed"
        raise self.retry(exc=exc)
    finally:
        delivery.save(update_fields=["status", "response_status", "response_body", "attempt"])