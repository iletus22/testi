from pathlib import Path
import argparse

from hetzner_ws_monitor.gui import run
from hetzner_ws_monitor.settings import Settings
from hetzner_ws_monitor.storage import Storage


def main(argv: list[str] | None = None) -> int:
    """Entry point for the monitor application."""

    parser = argparse.ArgumentParser(description="WebSocket monitor")
    parser.add_argument("--url", help="WebSocket URL")
    parser.add_argument("--no-db", action="store_true", help="Disable database storage")
    args = parser.parse_args(argv)

    settings = Settings()
    url = args.url or settings.get("url")
    storage = None
    if not args.no_db and settings.get("save_to_db", True):
        storage = Storage(Path("data.db"))

    try:
        return run(url=url, storage=storage)
    except KeyboardInterrupt:
        return 0
    finally:
        if storage is not None:
            storage.close()


if __name__ == "__main__":
    raise SystemExit(main())
