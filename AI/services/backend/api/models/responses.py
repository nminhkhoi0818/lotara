"""Response models for the API."""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ItineraryResponse(BaseModel):
    """Response model for itinerary generation."""
    
    status: str = Field(..., description="Request status: pending, processing, completed, failed")
    session_id: str = Field(..., description="Session ID for tracking")
    user_id: str = Field(..., description="User ID")
    itinerary: Optional[Dict[str, Any]] = Field(None, description="Generated itinerary data")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "session_id": "sess_abc123",
                "user_id": "user-123",
                "itinerary": {
                    "trip_name": "Vietnam Cultural Journey",
                    "start_date": "2026-02-11",
                    "end_date": "2026-02-16",
                    "total_days": "5",
                    "trip_overview": []
                },
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model: str = Field(..., description="AI model being used")
    opik_enabled: bool = Field(..., description="Opik tracking status")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")
