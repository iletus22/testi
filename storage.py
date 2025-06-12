from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict


class Storage:
    """Simple SQLite based message storage."""

    def __init__(self, db_path: Path) -> None:
        """Create a connection and ensure the ``messages`` table exists."""

        self.db_path = db_path
        self.connection = sqlite3.connect(str(db_path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY,
                source TEXT,
                ts TEXT,
                content TEXT
            )
            """
        )
        self.connection.commit()

    def save_message(self, source: str, ts: datetime, content: str) -> None:
        """Persist a message to the database."""

        if self.connection is None:
            raise RuntimeError("Storage is closed")

        self.connection.execute(
            "INSERT INTO messages (source, ts, content) VALUES (?, ?, ?)",
            (source, ts.isoformat(), content),
        )
        self.connection.commit()

    def get_last(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the ``limit`` most recent messages (newest first)."""

        if self.connection is None:
            raise RuntimeError("Storage is closed")

        cursor = self.connection.execute(
            "SELECT id, source, ts, content FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close the underlying SQLite connection."""

        if self.connection is not None:
            self.connection.close()
            self.connection = None

