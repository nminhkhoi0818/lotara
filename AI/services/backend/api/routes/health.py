"""Health check endpoint."""

import sys
import os
from fastapi import APIRouter
from services.backend.api.models import HealthResponse

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.tracking import get_tracer

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for deployment monitoring."""
    settings = get_settings()
    tracer = get_tracer()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model=settings.model,
        opik_enabled=tracer is not None
    )
