from __future__ import annotations

import json
from typing import TYPE_CHECKING

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from apps.workspaces.models import Membership

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AbstractUser as UserType


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        token = self.scope.get("query_string", b"").decode().split("token=")[-1]
        if not token:
            await self.close(code=4001)
            return

        try:
            self.user = await self._authenticate_token(token)
        except (InvalidToken, TokenError):
            await self.close(code=4001)
            return

        self.groups = await self._get_workspace_groups(self.user)
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def task_update(self, event: dict[str, object]) -> None:
        await self.send(text_data=json.dumps(event["payload"]))

    @database_sync_to_async
    def _authenticate_token(self, token: str) -> UserType:
        from django.contrib.auth import get_user_model  
        User = get_user_model()
        valid = AccessToken(token)
        return User.objects.get(id=valid["user_id"])

    @database_sync_to_async
    def _get_workspace_groups(self, user: UserType) -> list[str]:
        ws_ids = Membership.objects.filter(user=user).values_list("workspace_id", flat=True)
        return [f"workspace_{ws_id}" for ws_id in ws_ids]