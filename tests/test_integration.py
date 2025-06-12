import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add project root and src to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from hetzner_ws_monitor.websocket_client import WebSocketClient
from storage import Storage
import websockets


@pytest.mark.asyncio
async def test_integration(tmp_path):
    messages = []

    async def echo(websocket):
        async for msg in websocket:
            messages.append(msg)
            await websocket.send(msg)

    server = await websockets.serve(echo, "127.0.0.1", 8765)
    try:
        storage = Storage(tmp_path / "data.db")
        client = WebSocketClient("ws://127.0.0.1:8765", storage=storage, reconnect_delay=0.1)
        await client.connect()
        await client.send("one")
        await client.send("two")

        async def wait_for_messages():
            for _ in range(50):
                if len(storage.get_last(limit=2)) >= 2:
                    return
                await asyncio.sleep(0.05)
            raise AssertionError("messages not stored")

        await wait_for_messages()
        await client.close()

        stored = [m["content"] for m in storage.get_last(limit=2)]
        assert stored == ["two", "one"]
    finally:
        server.close()
        await server.wait_closed()
        storage.close()
