from __future__ import annotations

import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from apps.tasks.models import Task

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="flowstate.notify_status_change",
)
def notify_status_change(
    self,
    task_id: str,
    actor_id: int,
    old_status: str,
    new_status: str,
) -> None:
    try:
        task = Task.objects.select_related("assignee", "project").get(id=task_id)
        assignee = task.assignee
        if not assignee or assignee.id == actor_id:
            logger.debug("Skipping notification: unassigned or self-modified task %s", task_id)
            return

        subject = f"Task '{task.title}' moved to {task.get_status_display()}"
        message = (
            f"Task '{task.title}' in project '{task.project.name}' "
            f"was moved from '{old_status}' to '{new_status}' "
            f"by user #{actor_id}."
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[assignee.email],
            fail_silently=False,
        )
        logger.info("Notification sent for task %s to %s", task_id, assignee.email)
    except Task.DoesNotExist:
        logger.error("Task %s not found for notification", task_id)
    except Exception as exc:
        logger.exception("Failed to send notification for task %s", task_id)
        raise self.retry(exc=exc)