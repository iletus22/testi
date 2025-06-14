# Hetzner WebSocket Monitor

[![CI](https://img.shields.io/github/actions/workflow/status/iletus22/testi/ci.yml?branch=main)](https://github.com/iletus22/testi/actions)
[![Docker](https://img.shields.io/badge/docker-image-blue)](https://github.com/iletus22/testi)

Simple desktop monitor for WebSocket feeds built with PySide6.

## Quick start

```bash
pipx install 'git+https://github.com/iletus22/testi'
monitor --url wss://echo.websocket.events
```

## Development

Install dependencies and run tests:

```bash
python -m pip install -e ".[dev]"
pytest -q
```

The application code lives under `src/hetzner_ws_monitor/`.
