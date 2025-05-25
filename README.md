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

## Configuration

Edit `config.js` and specify the WebSocket endpoint you want to use:

```javascript
module.exports = {
  endpoint: 'wss://your.server.example/ws'
};
```

## Running

Start the monitor from the command line:

```bash
npm start
```

Once started, the monitor will connect to the configured server and display
incoming messages in your terminal.
