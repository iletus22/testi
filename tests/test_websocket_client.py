import types
import asyncio
import sys
import os
import pytest

# Allow importing the package from the ``src`` directory without installing it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hetzner_ws_monitor.websocket_client import WebSocketClient


class DummyConnection:
    def __init__(self):
        self.sent = []
        self.closed = False

    async def send(self, message):
        self.sent.append(message)

    async def recv(self):
        return "data"

    async def close(self):
        self.closed = True


class FailingConnection(DummyConnection):
    def __init__(self):
        super().__init__()
        self.fail = True

    async def send(self, message):
        if self.fail:
            self.fail = False
            raise RuntimeError("connection lost")
        await super().send(message)


class MessageConnection(DummyConnection):
    def __init__(self, messages):
        super().__init__()
        self.messages = list(messages)

    async def recv(self):
        if not self.messages:
            raise RuntimeError("connection closed")
        return self.messages.pop(0)


class FailingRecvConnection(DummyConnection):
    def __init__(self):
        super().__init__()
        self.fail = True

    async def recv(self):
        if self.fail:
            self.fail = False
            raise RuntimeError("connection lost")
        return await super().recv()


def make_websockets_module(connections):
    ws = types.SimpleNamespace()

    async def connect(url):
        return connections.pop(0)

    ws.connect = connect
    return ws


def test_send_message(monkeypatch):
    async def inner():
        conn = DummyConnection()
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn]))

        client = WebSocketClient("ws://test")
        await client.connect()
        await client.send("hello")

        assert conn.sent == ["hello"]

    asyncio.run(inner())


def test_receive_message(monkeypatch):
    async def inner():
        conn = MessageConnection(["hello"])
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn]))

        client = WebSocketClient("ws://test")
        await client.connect()
        msg = await client.receive()

        assert msg == "hello"

    asyncio.run(inner())


def test_async_context_manager(monkeypatch):
    async def inner():
        conn = DummyConnection()
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn]))

        async with WebSocketClient("ws://test") as client:
            assert client.connection is conn
        assert conn.closed is True

    asyncio.run(inner())


def test_reconnect_on_send_error(monkeypatch):
    async def inner():
        conn1 = FailingConnection()
        conn2 = DummyConnection()
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn1, conn2]))

        client = WebSocketClient("ws://test", reconnect=True)
        await client.connect()
        await client.send("hello")

        assert conn1.closed is True
        assert conn2.sent == ["hello"]

    asyncio.run(inner())


def test_reconnect_on_receive_error(monkeypatch):
    async def inner():
        conn1 = FailingRecvConnection()
        conn2 = MessageConnection(["ok"])
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn1, conn2]))

        client = WebSocketClient("ws://test", reconnect=True)
        await client.connect()
        msg = await client.receive()

        assert conn1.closed is True
        assert msg == "ok"

    asyncio.run(inner())


def test_close_gracefully(monkeypatch):
    async def inner():
        conn = DummyConnection()
        monkeypatch.setitem(sys.modules, "websockets", make_websockets_module([conn]))

        client = WebSocketClient("ws://test")
        await client.connect()
        await client.close()

        assert conn.closed is True
        assert client.connection is None

    asyncio.run(inner())
