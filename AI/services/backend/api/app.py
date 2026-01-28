"""FastAPI application for Lotara Travel Agent."""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.tracking import flush_traces
from api.routes import itinerary_router, health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    # Startup
    settings = get_settings()
    print(f"[STARTUP] Lotara Travel Agent API")
    print(f"[STARTUP] Environment: {settings.environment}")
    print(f"[STARTUP] Model: {settings.model}")
    print(f"[STARTUP] Opik Project: {settings.opik_project}")
    
    yield
    
    # Shutdown
    print("[SHUTDOWN] Flushing Opik traces...")
    flush_traces()
    print("[SHUTDOWN] Lotara Travel Agent API stopped")


# Initialize FastAPI app
app = FastAPI(
    title="Lotara Travel Agent API",
    description="AI-powered travel itinerary generation using multi-agent system",
    version="1.0.0",
    lifespan=lifespan
)

# Load settings for CORS
settings = get_settings()
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": str(exc)[:200] if settings.environment == "development" else None
        }
    )


# Include routers
app.include_router(health_router)
app.include_router(itinerary_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Lotara Travel Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
