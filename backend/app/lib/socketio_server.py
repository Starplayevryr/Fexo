# app/lib/socketio_server.py
import socketio

# -------------------------------
# Initialize Socket.IO server
# -------------------------------
# This is a global AsyncServer instance used across the app
# It supports ASGI (FastAPI) and allows async event handling.

sio = socketio.AsyncServer(
    async_mode="asgi",         # Use ASGI mode for compatibility with FastAPI
    cors_allowed_origins="*",   # Allow connections from any origin (adjust for production)
)
