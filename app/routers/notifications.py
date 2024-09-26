from fastapi import APIRouter, WebSocket, Depends
from fastapi.websockets import WebSocketDisconnect
from app import schemas
from app.dependencies import get_current_user
from typing import List

router = APIRouter(
    prefix="/ws",
    tags=["websockets"],
)

active_connections: List[WebSocket] = []

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, user: schemas.User = Depends(get_current_user)):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_message(message: str):
    for connection in active_connections:
        await connection.send_text(message)