class WebSocketClient:
    """Minimal asynchronous WebSocket client."""

    def __init__(self, url: str, reconnect: bool = False) -> None:
        self.url = url
        self.connection = None
        self.reconnect = reconnect

    async def connect(self) -> None:
        """Establish a WebSocket connection."""
        # ``websockets`` is imported lazily so tests can stub it easily.
        import websockets  # type: ignore

        self.connection = await websockets.connect(self.url)

    async def _reconnect(self) -> None:
        await self.close()
        await self.connect()

    async def send(self, message: str) -> None:
        """Send ``message`` if a connection exists."""
        if self.connection is None:
            raise RuntimeError("Not connected")

        try:
            await self.connection.send(message)
        except Exception:
            if self.reconnect:
                await self._reconnect()
                await self.connection.send(message)
            else:
                raise

    async def receive(self) -> str:
        """Receive a message if a connection exists."""
        if self.connection is None:
            raise RuntimeError("Not connected")

        try:
            return await self.connection.recv()
        except Exception:
            if self.reconnect:
                await self._reconnect()
                return await self.connection.recv()
            raise

    async def close(self) -> None:
        """Close the connection if present."""
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def __aenter__(self) -> "WebSocketClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
