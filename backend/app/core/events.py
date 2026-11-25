import asyncio
import json
from typing import Set, Dict, Any
from starlette.websockets import WebSocket

class EventBroadcaster:
    """Manages real-time WebSocket connections and broadcasts security events."""

    def __init__(self):
        self._active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self._active_connections:
                self._active_connections.remove(websocket)

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcasts event payload to all connected clients."""
        payload = json.dumps({"type": event_type, "data": data}, default=str)
        async with self._lock:
            connections = list(self._active_connections)

        for connection in connections:
            try:
                await connection.send_text(payload)
            except Exception:
                await self.disconnect(connection)

broadcaster = EventBroadcaster()
