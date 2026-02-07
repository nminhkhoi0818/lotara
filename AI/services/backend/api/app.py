"""FastAPI application for Lotara Travel Agent."""

import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import routes (lightweight, no heavy dependencies)
from services.backend.api.routes import itinerary_router, health_router

# Global semaphore to limit concurrent requests (prevent overload)
# Configurable via environment variable (default: 2 for production, 3 for dev)
import os as _os
MAX_CONCURRENT_REQUESTS = int(_os.getenv("MAX_CONCURRENT_REQUESTS", "2"))
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

print(f"[INIT] Request semaphore initialized: {MAX_CONCURRENT_REQUESTS} concurrent requests max")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    # Lazy import settings to reduce cold start
    from src.travel_lotara.config.settings import get_settings
    
    # Startup
    settings = get_settings()
    print(f"[STARTUP] Lotara Travel Agent API")
    print(f"[STARTUP] Environment: {settings.environment}")
    print(f"[STARTUP] Model: {settings.model}")
    print(f"[STARTUP] Max Concurrent Requests: {MAX_CONCURRENT_REQUESTS}")
    print(f"[STARTUP] Opik Project: {settings.opik_project_name}")
    print(f"[STARTUP] Opik Workspace: {settings.opik_workspace_name}")
    
    # Pre-warm Milvus connection with optimized warmup
    try:
        from src.travel_lotara.tools.shared_tools.milvus_engine import initialize_milvus
        
        # Initialize Milvus with connection warmup
        stats = initialize_milvus(warmup=True)
        
        print(f"[STARTUP] Milvus initialized: {stats.get('count', 0)} locations available")
        if stats.get('exists'):
            print("[STARTUP] Milvus connection pre-warmed successfully")
        else:
            print("[STARTUP WARNING] Milvus collection not found - run setup_milvus.py")
    except Exception as e:
        print(f"[STARTUP WARNING] Failed to initialize Milvus: {e}")
    
    yield
    
    # Shutdown - lazy import for flush
    from src.travel_lotara.tracking import flush_traces
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

# Load CORS settings - MUST configure before adding middleware
# For development, allow all origins. For production, specify allowed origins via CORS_ORIGINS env var
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    cors_origins = ["*"]
else:
    cors_origins = cors_origins_env.split(",")

print(f"[INIT] CORS origins: {cors_origins}")

# Add CORS middleware - MUST be added FIRST before other middleware and routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    # Lazy import settings
    from src.travel_lotara.config.settings import get_settings
    settings = get_settings()
    
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
