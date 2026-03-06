from fastapi import WebSocket
from typing import Dict
from auth import auth_service
from database.database_control import DB

class WebSocketManager:
    def __init__(self):
        self.connected_clients: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket):

        await websocket.accept()


        token = websocket.query_params.get("token")
        user = auth_service.get_current_user(token)
        if not user:
            print("WebSocket connection rejected: Invalid token")
            return

        self.connected_clients[user.get("id")] = websocket

        print("All connected clients:", self.connected_clients)

    async def send_message_all(self, sender_websocket: WebSocket, message: dict, db: DB):
        sender_uid = self.get_id_by_websocket(sender_websocket)

        if sender_uid is None:
            print("WebSocket not found in connected clients")
            return

        user = db.get_user_by_id(sender_uid)
        if not user:
            print("User not found")
            return

        username = user[1]

        full_message = {
            "user": username,
            "message": message
        }
        print(self.connected_clients)

        for user_id, client in self.connected_clients.items():
            if client == sender_websocket:
                continue
            client.send_json(full_message)

    async def send_message(self, sender_websocket: WebSocket, target_websocket: WebSocket, data: dict, db: DB):
        sender_uid = self.get_id_by_websocket(sender_websocket)
        if sender_uid is None:
            print("WebSocket not found in connected clients")
            return

        user = db.get_user_by_id(sender_uid)
        if not user:
            print("User not found")
            return

        username = user[1]

        full_message = {
            "id": sender_uid,
            "user": username,
            **data
        }

        await target_websocket.send_json(full_message)

    async def disconnect(self, websocket: WebSocket):
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!client disconnected - {websocket.client.host}:{websocket.client.port}")
        for user_id, client in self.connected_clients.items():
            if client == websocket:
                del self.connected_clients[user_id]
                break

    def get_id_by_websocket(self, websocket: WebSocket) -> int | None:
        for user_id, client in self.connected_clients.items():
            if client == websocket:
                return user_id
        return None