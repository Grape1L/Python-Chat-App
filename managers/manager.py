from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.connected_clients: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        
        print(f"------------------------------------------------------------new client connected - {websocket.client.host}:{websocket.client.port}")
        self.connected_clients.append(websocket)
        print(f"connected clients: {self.connected_clients}")

    async def send_message_all(self, websocket: WebSocket, message: dict):
        full_message = {
            "client": f"{websocket.client.host}:{websocket.client.port}",
            "message": message
        }

        for client in self.connected_clients:
            if client == websocket:
                continue
            await client.send_json(full_message)

    async def send_message(self, websocket: WebSocket, message: dict):
        full_message = {
            "client": f"{websocket.client.host}:{websocket.client.port}",
            "message": message
        }

        await websocket.send_json(full_message)

    async def disconnect(self, websocket: WebSocket):
        print(f"client disconnected - {websocket.client.host}:{websocket.client.port}")
        self.connected_clients.remove(websocket)