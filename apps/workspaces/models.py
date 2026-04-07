from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="owned_workspaces",
        verbose_name=_("Owner"),
        help_text=_("Creator & primary admin. Multi-user access handled via Membership (Phase 3.3).")
    )
    name = models.CharField(max_length=255, verbose_name=_("Workspace Name"))
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workspaces"
        verbose_name = _("Workspace")
        verbose_name_plural = _("Workspaces")
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(fields=["slug"], name="uq_workspace_slug"),
        ]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            base = self.name.lower().replace(" ", "-")
            self.slug = f"{base}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
        
class MembershipRole(models.TextChoices):
    ADMIN = "admin", _("Admin")
    MEMBER = "member", _("Member")
    VIEWER = "viewer", _("Viewer")

class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships"
    )
    role = models.CharField(
        max_length=10,
        choices=MembershipRole.choices,
        default=MembershipRole.VIEWER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workspace_memberships"
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(fields=["workspace", "user"], name="uq_membership_workspace_user"),
        ]
        indexes = [
            models.Index(fields=["user", "role"]),
            models.Index(fields=["workspace", "role"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} → {self.workspace.name} ({self.role})"