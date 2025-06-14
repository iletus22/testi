import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import pytest

# Ensure the project root is on ``sys.path`` so ``storage`` can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from hetzner_ws_monitor.storage import Storage


def test_save_and_get_last(tmp_path):
    db = tmp_path / "data.db"
    s = Storage(db)
    s.save_message("a", datetime(2022, 1, 1, 12, 0, 0), "hello")
    s.save_message("b", datetime(2022, 1, 1, 13, 0, 0), "world")
    msgs = s.get_last()
    assert [m["content"] for m in msgs] == ["world", "hello"]
    s.close()


def test_limit(tmp_path):
    db = tmp_path / "db.sqlite"
    s = Storage(db)
    for i in range(100):
        s.save_message("src", datetime(2022, 1, 1) + timedelta(minutes=i), f"m{i}")
    msgs = s.get_last(limit=10)
    assert len(msgs) == 10
    assert msgs[0]["content"] == "m99"
    assert msgs[-1]["content"] == "m90"
    s.close()


def test_init_creates_table(tmp_path):
    db = tmp_path / "db.sqlite"
    s = Storage(db)
    cur = s.connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
    assert cur.fetchone() is not None
    s.close()


def test_close(tmp_path):
    db = tmp_path / "db.sqlite"
    s = Storage(db)
    s.close()
    with pytest.raises(RuntimeError):
        s.save_message("x", datetime.now(), "y")
