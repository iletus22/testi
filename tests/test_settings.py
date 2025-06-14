import os
import sys
import json
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from hetzner_ws_monitor.settings import Settings


def test_defaults_created(tmp_path):
    path = tmp_path / "settings.json"
    s = Settings(path)
    assert s.get("url") == "wss://example.com/feed"
    assert s.get("save_to_db") is True
    data = json.loads(path.read_text())
    assert data["url"] == "wss://example.com/feed"
    assert data["save_to_db"] is True


def test_merge_existing(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"url": "ws://custom"}')
    s = Settings(path)
    assert s.get("url") == "ws://custom"
    assert s.get("save_to_db") is True
    data = json.loads(path.read_text())
    assert data["save_to_db"] is True


def test_set_persists(tmp_path):
    path = tmp_path / "settings.json"
    s = Settings(path)
    s.set("url", "ws://changed")
    s2 = Settings(path)
    assert s2.get("url") == "ws://changed"
