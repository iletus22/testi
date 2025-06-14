from __future__ import annotations

import asyncio
import sys
from typing import Optional

from PySide6.QtCore import QMetaObject, Qt, Q_ARG, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QAction,
    QApplication,
    QListWidget,
    QMainWindow,
)

from hetzner_ws_monitor import WebSocketClient
from .storage import Storage


class _ClientThread(QThread):
    """Run :class:`WebSocketClient` inside a QThread."""

    message_received = Signal(str)
    connection_state = Signal(bool)

    def __init__(self, url: str, storage: Optional[Storage]) -> None:
        super().__init__()
        self.url = url
        self.storage = storage
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._client: Optional[WebSocketClient] = None

    def run(self) -> None:  # pragma: no cover - Qt thread
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._client = WebSocketClient(self.url, storage=self.storage)
        self._client.add_callback(self._on_message)

        async def start() -> None:
            await self._client.connect()
            self.connection_state.emit(True)

        self._loop.run_until_complete(start())
        try:
            self._loop.run_forever()
        finally:
            self._loop.run_until_complete(self._client.close())
            self.connection_state.emit(False)
            self._loop.close()

    def stop(self) -> None:
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self.wait()

    @Slot(str)
    def _emit(self, message: str) -> None:
        self.message_received.emit(message)

    async def _on_message(self, message: str) -> None:
        QMetaObject.invokeMethod(
            self,
            "_emit",
            Qt.QueuedConnection,
            Q_ARG(str, message),
        )


class MainWindow(QMainWindow):
    """Simple monitor window with a message list."""

    def __init__(self, url: str, storage: Optional[Storage] = None) -> None:
        super().__init__()
        self.setWindowTitle("Monitor")

        self.list_widget = QListWidget()
        self.setCentralWidget(self.list_widget)

        self.statusBar().showMessage("Yhteys katkennut")

        self._paused = False
        self._client_thread = _ClientThread(url, storage)
        self._client_thread.message_received.connect(self.add_message)
        self._client_thread.connection_state.connect(self.update_status)

        if storage is not None:
            for msg in reversed(storage.get_last(limit=100)):
                self.list_widget.addItem(msg["content"])

        self._create_menu()
        self._client_thread.start()

    # ------------------------------------------------------------------ menu
    def _create_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu.addMenu("View")
        self.pause_action = QAction("Pause feed", self, checkable=True)
        view_menu.addAction(self.pause_action)

    # ------------------------------------------------------------------ slots
    @Slot(str)
    def add_message(self, message: str) -> None:
        if self.pause_action.isChecked():
            return
        self.list_widget.insertItem(0, message)
        while self.list_widget.count() > 500:
            self.list_widget.takeItem(self.list_widget.count() - 1)

    @Slot(bool)
    def update_status(self, connected: bool) -> None:
        self.statusBar().showMessage("Yhdistetty" if connected else "Yhteys katkennut")

    # ------------------------------------------------------------------ events
    def closeEvent(self, event) -> None:  # pragma: no cover - Qt
        self._client_thread.stop()
        super().closeEvent(event)


def run(url: str, *, storage: Optional[Storage] = None) -> int:  # pragma: no cover - Qt
    """Launch the application."""

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(url, storage=storage)
    window.show()
    ret = app.exec()
    return ret

