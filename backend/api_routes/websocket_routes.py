from backend.managers.manager import WebSocketManager
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from backend.database.database_control import DB

router = APIRouter()
ws_manager = WebSocketManager()


def get_db_ws(websocket: WebSocket) -> DB:
    return websocket.app.state.db


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: DB = Depends(get_db_ws)):

    token = websocket.cookies.get("access_token")


    await ws_manager.connect(websocket, token)

    try:
        while True:
            data = await websocket.receive_json()
            target_user_ID = data.get("targetUser_ID")

            # Check if the message should be saved in the database
            disappear: bool = data.get("disappear")

            if disappear == False:
                db.save_message(
                    sender_id=ws_manager.get_id_by_websocket(websocket), 
                    recipient_id=target_user_ID, 
                    content=data.get("content")
                )


            target_websocket = ws_manager.connected_clients.get(str(target_user_ID))

            if not target_websocket:
                await ws_manager.send_message(websocket, websocket, {"error": "WebSocket not found"}, db)
                continue

            if data.get("type") == "key":
                await ws_manager.send_message(
                    websocket, 
                    target_websocket, 
                    {
                        "message": data.get("content"), 
                        "type": data.get("type"), 
                        "firstSender": data.get("firstSender")
                    }, 
                    db
                )
                continue


            await ws_manager.send_message(websocket, target_websocket, { "message": data.get("content"), "type": data.get("type") }, db)

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)