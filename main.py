from gui import run
from settings import Settings


def main() -> int:
    """Entry point for the monitor application."""

    settings = Settings()
    url = settings.get("url")
    save_to_db = settings.get("save_to_db", True)
    return run(url=url, save_to_db=save_to_db)


if __name__ == "__main__":
    main()
