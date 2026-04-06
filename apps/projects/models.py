from __future__ import annotations

import uuid

from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from apps.workspaces.models import Workspace


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", _("Planning")
        ACTIVE = "active", _("Active")
        ARCHIVED = "archived", _("Archived")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name=_("Workspace"),
    )
    name = models.CharField(max_length=255, verbose_name=_("Project Name"))
    slug = models.SlugField(max_length=255, allow_unicode=True)
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(
                fields=["workspace", "slug"],
                name="uq_project_workspace_slug"
            ),
        ]
        indexes = [
            models.Index(fields=["workspace", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.workspace.name} / {self.name}"

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            base = self.name.lower().replace(" ", "-")
            self.slug = f"{base}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)