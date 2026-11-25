from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.events import broadcaster

router = APIRouter(tags=["Realtime Events"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            # Keep-alive receive loop
            await websocket.receive_text()
    except WebSocketDisconnect:
        await broadcaster.disconnect(websocket)
    except Exception:
        await broadcaster.disconnect(websocket)
