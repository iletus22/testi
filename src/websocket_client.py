import asyncio
import logging
from typing import Awaitable, Callable, Optional

try:
    import websockets
except ModuleNotFoundError:  # pragma: no cover - library might not be installed
    websockets = None  # type: ignore


class WebSocketClient:
    """Simple asynchronous WebSocket client."""

    def __init__(self, url: str, message_handler: Callable[[str], Awaitable[None]]):
        self.url = url
        self.message_handler = message_handler
        self._connection: Optional["websockets.WebSocketClientProtocol"] = None
        self._task: Optional[asyncio.Task[None]] = None
        self._running = False

    async def connect(self) -> None:
        if websockets is None:
            raise RuntimeError("websockets library not available")
        self._connection = await websockets.connect(self.url)

    async def listen(self) -> None:
        if self._connection is None:
            await self.connect()
        assert self._connection is not None
        self._running = True
        try:
            async for message in self._connection:
                await self.message_handler(message)
        except (websockets.ConnectionClosed, RuntimeError) as exc:
            logging.info("WebSocket closed: %s", exc)
        finally:
            self._running = False

    async def run(self) -> None:
        await self.listen()

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self.run())

    async def stop(self) -> None:
        if self._connection is not None:
            await self._connection.close()
        if self._task is not None:
            await self._task
        self._running = False
