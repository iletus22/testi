# Hetzner-WebSocket Desktop Monitor

Hetzner-WebSocket Desktop Monitor is a small example project that shows how to
monitor a Hetzner server from a desktop application using a WebSocket
connection. The monitor listens for real-time updates and prints them to the
console.

## Setup

1. Clone this repository.
2. Install Python (3.8 or newer) and `pip`.
3. Install the project dependencies:
   ```bash
   pip install -e .
   ```
   To install test dependencies as well use:
   ```bash
   pip install -e .[test]
   ```

## Running

Run the application with:
```bash
python main.py
```

## Running Tests

The project uses `pytest`. To run the tests execute:
```bash
pytest
```
