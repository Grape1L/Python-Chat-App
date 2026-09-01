from fastapi import WebSocket
from typing import Dict
from backend.auth import auth_service
from backend.database.database_control import DB
import asyncio
import logging

class ConnectedClients:
    def __init__(self):
        self._id_to_ws: Dict[int, WebSocket] = {}
        self._ws_to_id: Dict[WebSocket, int] = {}

    def add_client(self, user_id: int, websocket: WebSocket):
        if type(user_id) is not int:
            raise ValueError("user_id must be int")
        
        if self._id_to_ws.get(user_id) is not None:
            self.remove_by_id(user_id)
        elif self._ws_to_id.get(websocket) is not None:
            self.remove_by_ws(websocket)

        self._id_to_ws[user_id] = websocket
        self._ws_to_id[websocket] = user_id

    def remove_by_id(self, user_id: int):
        websocket = self._id_to_ws.pop(user_id, None)
        self._ws_to_id.pop(websocket, None)

    def remove_by_ws(self, websocket: WebSocket):
        user_id = self._ws_to_id.pop(websocket, None)
        self._id_to_ws.pop(user_id, None)

    def get_websocket(self, user_id: int) -> WebSocket | None:
        return self._id_to_ws.get(user_id)
    
    def get_user_id(self, websocket: WebSocket) -> int | None:
        return self._ws_to_id.get(websocket)
    
    def get_all(self) -> Dict[int, WebSocket]:
        return self._id_to_ws
    
    def __len__(self) -> int:
        return len(self._id_to_ws)
    


class WebSocketManager:
    def __init__(self):
        self.connected_clients = ConnectedClients()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, token) -> bool:
        try:
            user = auth_service.verify_token(token)
        except Exception:
            print("WebSocket connection rejected: token verification raised")
            return False

        if not user:
            print("WebSocket connection rejected: Invalid token")
            return False

        async with self._lock:
            self.connected_clients.add_client(user.get("id"), websocket)

        await websocket.accept()
        
        return True


    async def send_message(self, sender_websocket: WebSocket, target_websocket: WebSocket, data: dict, db: DB):
        sender_uid = self.connected_clients.get_user_id(sender_websocket)
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
        async with self._lock:
            self.connected_clients.remove_by_ws(websocket)

        try:
            await websocket.close()
        except Exception:
            print("Error closing websocket during disconnecting")
            
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!client disconnected - {websocket.client.host}:{websocket.client.port}")