"""VoxSentinalX Main Application Entrypoint."""
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
