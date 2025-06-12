import asyncio
import types
import sys
import os

import pytest

# Allow importing package from ``src`` directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hetzner_ws_monitor.websocket_client import WebSocketClient


class DummyConnection:
    def __init__(self, messages=None, fail_on_recv=False):
        self.messages = list(messages or [])
        self.fail_on_recv = fail_on_recv
        self.closed = False
        self.recv_calls = 0

    async def send(self, message):
        pass

    async def recv(self):
        self.recv_calls += 1
        if self.fail_on_recv and self.recv_calls == 1:
            raise RuntimeError("connection lost")
        if not self.messages:
            raise RuntimeError("closed")
        return self.messages.pop(0)

    async def close(self):
        self.closed = True


def make_websockets_module(connections):
    ws = types.SimpleNamespace()

    async def connect(url):
        return connections.pop(0)

    ws.connect = connect
    return ws


class DummyStorage:
    def __init__(self):
        self.saved = []

    def save_message(self, source, ts, content):
        self.saved.append(content)


def test_callbacks_and_storage(monkeypatch):
    async def inner():
        conn = DummyConnection(["a", "b", "c"])
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn]))

        storage = DummyStorage()
        received = []

        async def cb(msg):
            received.append(msg)

        client = WebSocketClient("ws://test", storage=storage, reconnect_delay=0.01)
        client.add_callback(cb)
        await client.connect()
        await asyncio.sleep(0.05)
        await client.close()

        assert received == ["a", "b", "c"]
        assert storage.saved == ["a", "b", "c"]

    asyncio.run(inner())


def test_reconnect_on_failure(monkeypatch):
    async def inner():
        conn1 = DummyConnection(fail_on_recv=True)
        conn2 = DummyConnection(["ok"])
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn1, conn2]))

        results = []
        client = WebSocketClient("ws://test", reconnect_delay=0.01)
        client.add_callback(lambda m: results.append(m))
        await client.connect()
        await asyncio.sleep(0.05)
        await client.close()

        assert conn1.closed is True
        assert results == ["ok"]

    asyncio.run(inner())


def test_context_manager(monkeypatch):
    async def inner():
        conn = DummyConnection(["x"])
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn]))

        async with WebSocketClient("ws://test", reconnect_delay=0.01) as client:
            await asyncio.sleep(0.01)
        assert conn.closed is True

    asyncio.run(inner())


