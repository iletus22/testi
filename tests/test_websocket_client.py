import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from websocket_client import WebSocketClient


def test_create_client():
    async def handler(msg: str) -> None:
        pass

    client = WebSocketClient("ws://example.com", handler)
    assert client.url == "ws://example.com"
    assert client.message_handler is handler
