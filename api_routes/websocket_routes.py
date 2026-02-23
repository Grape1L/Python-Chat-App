from managers.manager import WebSocketManager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
ws_manager = WebSocketManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_json()
            print(f"Message from client: {message}")
            
            await ws_manager.send_message_all(websocket, message)
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)