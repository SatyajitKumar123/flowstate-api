from __future__ import annotations
from typing import Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_task_update(task, action: str, payload: dict[str, Any]) -> None:
    channel_layer = get_channel_layer()
    workspace = task.project.workspace
    group_name = f"workspace_{workspace.slug}"
    payload = {
        "type": "task_update",
        "data": {
            "action": action,
            "workspace_slug": workspace.slug,
            "task": payload,
        }
    }
    async_to_sync(channel_layer.group_send)(group_name, payload)