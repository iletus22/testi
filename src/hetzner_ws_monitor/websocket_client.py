from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Any, Callable, List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from .storage import Storage


class WebSocketClient:
    """Asynchronous WebSocket client with reconnection and callbacks."""

    def __init__(self, url: str, storage: Optional["Storage"] = None, reconnect_delay: float = 3.0) -> None:
        self.url = url
        self.storage = storage
        self.reconnect_delay = reconnect_delay
        self.connection = None
        self._receive_task: Optional[asyncio.Task] = None
        self._callbacks: List[Callable[[str], Any]] = []
        self._running = False

    async def connect(self) -> None:
        """Establish a WebSocket connection and start receive loop."""
        await self._establish_connection()
        self._running = True
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def _establish_connection(self) -> None:
        import websockets  # type: ignore
        headers: Dict[str, str] = {}
        token = os.environ.get("HETZNER_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.connection = await websockets.connect(
            self.url, extra_headers=headers or None
        )

    async def send(self, message: str) -> None:
        """Send ``message`` if a connection exists."""
        if self.connection is None:
            raise RuntimeError("Not connected")

        await self.connection.send(message)

    async def receive(self) -> str:
        """Receive a message if a connection exists."""
        if self.connection is None:
            raise RuntimeError("Not connected")

        return await self.connection.recv()

    async def close(self) -> None:
        """Close the connection and stop the receive loop."""
        self._running = False
        if self._receive_task is not None:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None

        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def __aenter__(self) -> "WebSocketClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    def add_callback(self, callback: Callable[[str], Any]) -> None:
        """Register a callback invoked for every received message."""
        self._callbacks.append(callback)

    async def _handle_message(self, message: str) -> None:
        if self.storage is not None:
            self.storage.save_message(self.url, datetime.utcnow(), message)

        for cb in self._callbacks:
            try:
                result = cb(message)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                # Callback errors are ignored
                pass

    async def _receive_loop(self) -> None:
        delay = self.reconnect_delay
        while self._running:
            try:
                message = await self.connection.recv()
                await self._handle_message(message)
                delay = self.reconnect_delay
            except asyncio.CancelledError:
                break
            except Exception:
                if not self._running:
                    break
                try:
                    await self.connection.close()
                except Exception:
                    pass
                self.connection = None
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30.0)
                try:
                    await self._establish_connection()
                except Exception:
                    # Connection failed, loop will retry
                    continue
