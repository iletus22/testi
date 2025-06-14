import os
import pytest

if os.environ.get('DISPLAY', '') == '':
    pytest.skip('No display available', allow_module_level=True)

from PySide6.QtWidgets import QApplication
from hetzner_ws_monitor.gui import MainWindow


def test_mainwindow_basic():
    _app = QApplication.instance() or QApplication([])
    w = MainWindow("ws://test")
    assert w.list_widget.count() >= 0
    w.close()
