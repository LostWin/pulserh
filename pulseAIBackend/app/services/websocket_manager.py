import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("pulse.services.websocket_manager")


class WebSocketManager:
    def __init__(self):
        self.user_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.role_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.connection_meta: dict[WebSocket, dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, roles: list[str]) -> None:
        await websocket.accept()
        self.user_connections[user_id].add(websocket)
        for role in roles:
            self.role_connections[role].add(websocket)
        self.connection_meta[websocket] = {"user_id": user_id, "roles": roles}
        logger.info("WebSocket connected for user %s with roles %s", user_id, roles)

    def disconnect(self, websocket: WebSocket) -> None:
        meta = self.connection_meta.pop(websocket, None)
        if not meta:
            return

        user_id = meta["user_id"]
        roles = meta["roles"]
        self.user_connections[user_id].discard(websocket)
        if not self.user_connections[user_id]:
            self.user_connections.pop(user_id, None)

        for role in roles:
            self.role_connections[role].discard(websocket)
            if not self.role_connections[role]:
                self.role_connections.pop(role, None)

    async def broadcast_alert(
        self,
        event_type: str,
        alert: dict[str, Any],
        target_user_id: str | None = None,
        target_roles: list[str] | None = None,
    ) -> None:
        payload = {"type": event_type, "alert": alert}
        recipients = set()

        if target_user_id:
            recipients.update(self.user_connections.get(target_user_id, set()))
        for role in target_roles or []:
            recipients.update(self.role_connections.get(role, set()))

        stale_connections = []
        for websocket in recipients:
            try:
                await websocket.send_json(payload)
            except Exception as error:
                logger.warning("WebSocket send failed: %s", error)
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(websocket)

    async def broadcast_user_event(self, event_type: str, user_id: str, data: dict[str, Any]) -> None:
        payload = {"type": event_type, **data}
        stale_connections = []
        for websocket in self.user_connections.get(user_id, set()):
            try:
                await websocket.send_json(payload)
            except Exception as error:
                logger.warning("WebSocket send failed: %s", error)
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(websocket)


websocket_manager = WebSocketManager()
