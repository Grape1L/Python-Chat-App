import pytest
from types import SimpleNamespace
from backend.managers.manager import ConnectedClients

class FakeWebSocket:
    def __init__(self):
        self.client = SimpleNamespace(host="127.0.0.1", port=12345)


connected_clients = ConnectedClients()
ws = FakeWebSocket()



def test_add_client():
    connected_clients.add_client(9, ws)