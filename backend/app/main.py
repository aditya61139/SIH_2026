import os
import sys

# Ensure workspace root and backend directory are in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router
from app.api.websocket_handler import router as ws_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks (SIH 26104)",
)

# Configure CORS for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR, tags=["API"])
app.include_router(ws_router, tags=["WebSocket Streaming"])


@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "VoxSentinalX Real-Time Voice Cloning Detection Engine",
        "endpoints": {
            "health": f"{settings.API_V1_STR}/health",
            "config": f"{settings.API_V1_STR}/config",
            "file_analysis": f"{settings.API_V1_STR}/analyze-file",
            "websocket_stream": "/ws/analyze",
        },
    }
