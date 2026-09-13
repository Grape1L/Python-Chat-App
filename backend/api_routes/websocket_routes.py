from backend.managers.manager import WebSocketManager, ConnectedClients
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from backend.database.database_control import DB
from backend.exceptions.token import InvalidToken, TokenVerification

router = APIRouter()
connected_clients = ConnectedClients()


def get_db_ws(websocket: WebSocket) -> DB:
    return websocket.app.state.db


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: DB = Depends(get_db_ws)):
    ws_manager = WebSocketManager(websocket, connected_clients)

    token = websocket.cookies.get("access_token")

    try:
        await ws_manager.connect(token)

    except (InvalidToken, TokenVerification):
        return
    

    try:
        while True:
            data = await websocket.receive_json()

            target_user_id = data.get("targetUser_ID")

            user = db.get_user_by_id(ws_manager.client_user_id)
            if not user:
                await ws_manager.send_error("User not found")
                continue

            if not db.are_friends(ws_manager.client_user_id, target_user_id):
                await ws_manager.send_error("You are not friends with this user")
                continue

            target_websocket = ws_manager.connected_clients.get_websocket(int(target_user_id))
            if not target_websocket:
                await ws_manager.send_error("Target websocket not found")
                continue


            if data.get("type") == "key":
                await ws_manager.send_message(
                    ws_manager.client_user_id, 
                    user, 
                    target_websocket, 
                    {
                        "message": data.get("content"), 
                        "type": data.get("type"), 
                        "firstSender": data.get("firstSender")
                    }
                )
                continue
      

            await ws_manager.send_message(
                ws_manager.client_user_id, 
                user, 
                target_websocket, 
                { 
                    "message": data.get("content"), 
                    "type": data.get("type") 
                }
            )

            # Check if the message should be saved in the database
            disappear: bool = data.get("disappear")

            if not disappear:
                db.save_message(
                    ws_manager.client_user_id, 
                    target_user_id, 
                    data.get("content")
                )

    except WebSocketDisconnect:
        pass

    finally:
        await ws_manager.disconnect()