# Hetzner-WebSocket Desktop Monitor

Hetzner-WebSocket Desktop Monitor is a small example project that shows how to
monitor a Hetzner server from a desktop application using a WebSocket
connection. The monitor listens for real-time updates and prints them to the
console.

## Setup

1. Clone this repository.
2. Install Node.js (version 16 or newer).
3. Install the project dependencies:
   ```bash
   npm install
   ```

## Dependencies

The project relies on the `ws` package for WebSocket communication. Running
`npm install` will download it automatically along with any other libraries
required by the example.

## Running

1. Edit `config.js` to specify your Hetzner WebSocket endpoint.
2. Start the monitor with:
   ```bash
   node monitor.js
   ```

Once started, the monitor will connect to the configured server and display
incoming messages in your terminal.
