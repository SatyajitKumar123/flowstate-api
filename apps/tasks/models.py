from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.projects.models import Project


class Task(models.Model):
    class Status(models.TextChoices):
        BACKLOG = "backlog", _("Backlog")
        TODO = "todo", _("To Do")
        IN_PROGRESS = "in_progress", _("In Progress")
        DONE = "done", _("Done")
        ARCHIVED = "archived", _("Archived")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks", verbose_name=_("Project")
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.TODO, db_index=True
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM, db_index=True
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name=_("Assignee"),
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="reported_tasks",
        verbose_name=_("Reporter"),
    )
    due_date = models.DateField(null=True, blank=True, verbose_name=_("Due Date"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assignee", "status"]),
            models.Index(fields=["reporter"]),
        ]

    def __str__(self) -> str:
        return f"[{self.get_status_display()}] {self.title}"


class TaskHistory(models.Model):
    class ChangeType(models.TextChoices):
        CREATED = "created", _("Created")
        UPDATED = "updated", _("Updated")
        STATUS_CHANGED = "status_changed", _("Status Changed")
        ASSIGNEE_CHANGED = "assignee_changed", _("Assignee Changed")
        DUE_DATE_CHANGED = "due_date_changed", _("Due Date Changed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="history", verbose_name=_("Task"))
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="task_history",
        verbose_name=_("Actor"),
    )
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)
    old_value = models.TextField(blank=True, default="", verbose_name=_("Old Value"))
    new_value = models.TextField(blank=True, default="", verbose_name=_("New Value"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_history"
        verbose_name = _("Task History")
        verbose_name_plural = _("Task History")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["task", "-created_at"])]