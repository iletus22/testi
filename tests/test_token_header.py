import os
import sys
import asyncio
import types

# add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hetzner_ws_monitor.websocket_client import WebSocketClient

class DummyConnection:
    async def send(self, message):
        pass
    async def recv(self):
        return "msg"
    async def close(self):
        pass

async def dummy_connect(url, extra_headers=None):
    dummy_connect.called_headers = extra_headers
    return DummyConnection()


def test_token_header(monkeypatch):
    os.environ["HETZNER_TOKEN"] = "token123"
    monkeypatch.setitem(sys.modules, "websockets", types.SimpleNamespace(connect=dummy_connect))

    async def inner():
        client = WebSocketClient("ws://example", reconnect_delay=0.01)
        await client.connect()
        await client.close()

    asyncio.run(inner())

    assert dummy_connect.called_headers == {"Authorization": "Bearer token123"}
    os.environ.pop("HETZNER_TOKEN")
