from __future__ import annotations

from django.contrib import admin

from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "status", "created_at")
    list_filter = ("status", "workspace__is_active")
    search_fields = ("name", "slug", "description", "workspace__name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("workspace",)
    ordering = ("-created_at",)
    list_select_related = ("workspace",)