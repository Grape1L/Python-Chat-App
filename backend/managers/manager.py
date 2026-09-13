from fastapi import WebSocket
from typing import Dict
from backend.auth import auth_service
import asyncio
import logging
from backend.exceptions.token import TokenVerification, InvalidToken
from fastapi import HTTPException

class ConnectedClients:
    def __init__(self):
        self._id_to_ws: Dict[int, WebSocket] = {}
        self._ws_to_id: Dict[WebSocket, int] = {}
        self._lock = asyncio.Lock()

    async def add_client(self, user_id: int, websocket: WebSocket):
        if type(user_id) is not int:
            raise ValueError("user_id must be int")
        
        async with self._lock:
            if self._id_to_ws.get(user_id) is not None:
                old_websocket = self._id_to_ws.pop(user_id, None)
                self._ws_to_id.pop(old_websocket, None)
            elif self._ws_to_id.get(websocket) is not None:
                old_user_id = self._ws_to_id.pop(websocket, None)
                self._id_to_ws.pop(old_user_id, None)

            self._id_to_ws[user_id] = websocket
            self._ws_to_id[websocket] = user_id

    async def remove_by_id(self, user_id: int):
        async with self._lock:
            websocket = self._id_to_ws.pop(user_id, None)
            self._ws_to_id.pop(websocket, None)

    async def remove_by_ws(self, websocket: WebSocket):
        async with self._lock:
            user_id = self._ws_to_id.pop(websocket, None)
            self._id_to_ws.pop(user_id, None)

    def get_websocket(self, user_id: int) -> WebSocket | None:
        return self._id_to_ws.get(user_id)
    
    def get_user_id(self, websocket: WebSocket) -> int | None:
        return self._ws_to_id.get(websocket)
    
    def __len__(self) -> int:
        return len(self._id_to_ws)
    


class WebSocketManager:
    def __init__(self, client_websocket: WebSocket, connected_clients: ConnectedClients):
        self.client_user_id = None
        self.client_websocket = client_websocket
        self.connected_clients = connected_clients

    async def connect(self, token):
        try:
            user = auth_service.verify_token(token)
        except HTTPException:
            raise TokenVerification("Token verification failed")

        if not user:
            raise InvalidToken("Invalid Token")
        
        self.client_user_id = int(user.get("id"))
        
        await self.client_websocket.accept()
        await self.connected_clients.add_client(self.client_user_id, self.client_websocket)


    async def send_to_client(self, data: dict):
        await self.client_websocket.send_json(data)

    async def send_error(self, message: str):
        await self.send_to_client({
            "type": "error",
            "message": message
        })

    async def send_message(self, sender_id, user, target_websocket: WebSocket, data: dict):
        username = user[1]

        full_message = {
            "id": sender_id,
            "user": username,
            **data
        }

        await target_websocket.send_json(full_message)

    async def disconnect(self, code: int = 1000):
        await self.connected_clients.remove_by_ws(self.client_websocket)

        try:
            await self.client_websocket.close(code=code)
        except RuntimeError:
            pass