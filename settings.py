from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class Settings:
    """Simple JSON-backed settings helper."""

    DEFAULTS: Dict[str, Any] = {
        "url": "wss://example.com/feed",
        "save_to_db": True,
    }

    def __init__(self, path: Path | str = Path("~/.hetzner_ws_monitor/settings.json")) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        else:
            data = {}

        self._data: Dict[str, Any] = {**self.DEFAULTS, **data}
        # persist defaults if keys were missing or file absent
        if data != self._data:
            self._write()

    # ------------------------------------------------------------------ utils
    def _write(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    # ------------------------------------------------------------------ mapping
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._write()

