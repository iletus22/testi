const WebSocket = require('ws');
const { endpoint } = require('./config');

const ws = new WebSocket(endpoint);

ws.on('open', () => {
  console.log(`Connected to ${endpoint}`);
});

ws.on('message', (data) => {
  console.log(`Message: ${data}`);
});

ws.on('error', (err) => {
  console.error('WebSocket error:', err.message);
});

ws.on('close', () => {
  console.log('Connection closed');
});
