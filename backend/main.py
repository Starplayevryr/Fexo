from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from app.lib.socketio_server import sio  # Import initialized Socket.IO server instance

from app.api import routes_upload, routes_extract, routes_process, routes_status
from socketio import ASGIApp

# Create FastAPI app instance
app = FastAPI(title="Doc LLM Pipeline with Socket.IO")

# Configure CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins (can be restricted later)
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"],        # Allow all headers
)

# Register API routers
app.include_router(routes_upload.router)   # Handles /upload endpoint
app.include_router(routes_extract.router)  # Handles /extract endpoint
app.include_router(routes_process.router)  # Handles /process endpoint
app.include_router(routes_status.router)   # Handles /status endpoint

# Wrap FastAPI app with Socket.IO support
app_sio = ASGIApp(sio, other_asgi_app=app)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

# Socket.IO connection event
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

# Socket.IO disconnection event
@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
