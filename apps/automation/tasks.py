from __future__ import annotations
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from apps.tasks.models import Task

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True, name="flowstate.notify_status_change")
def notify_status_change(self, task_id: str, actor_id: int, old_status: str, new_status: str) -> None:
    try:
        task = Task.objects.select_related("project").get(id=task_id)
        subject = f"Task '{task.title}' moved to {task.get_status_display()}"
        message = f"Task '{task.title}' was moved from '{old_status}' to '{new_status}' by user #{actor_id}."
        send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=["dev@localhost"], fail_silently=False)
        logger.info("✅ Notification sent for task %s", task_id)
    except Task.DoesNotExist:
        logger.error("Task %s not found", task_id)
    except Exception as exc:
        logger.exception("Failed: %s", task_id)
        raise self.retry(exc=exc)