"""Request models for the API."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class ItineraryRequest(BaseModel):
    """Request model for itinerary generation."""
    
    userId: str = Field(..., description="User ID for tracking and personalization")
    
    duration: Literal["short", "medium", "long", "extended"] = Field(
        ..., 
        description="Trip duration: short (3-5 days), medium (6-10 days), long (11-20 days), extended (21+ days)"
    )
    
    companions: Literal["solo", "couple", "family_kids", "family_adults", "friends"] = Field(
        ...,
        description="Travel companions type"
    )
    
    budget: Literal["budget", "midrange", "comfortable", "luxury"] = Field(
        ...,
        description="Budget level: budget ($30-50/day), midrange ($50-100/day), comfortable ($100-200/day), luxury ($200+/day)"
    )
    
    pace: Literal["slow", "balanced", "fast"] = Field(
        default="balanced",
        description="Travel pace preference"
    )
    
    travelStyle: Literal["adventure", "cultural", "nature", "food", "wellness", "photography"] = Field(
        ...,
        description="Primary travel style"
    )
    
    activity: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Activity intensity level"
    )
    
    crowds: Literal["avoid", "mixed", "embrace"] = Field(
        default="mixed",
        description="Crowd tolerance"
    )
    
    accommodation: Literal["hostel", "standard", "boutique", "premium"] = Field(
        default="standard",
        description="Accommodation preference"
    )
    
    remote: bool = Field(
        default=False,
        description="Prefer remote/off-beaten-path destinations"
    )
    
    timing: Literal["morning", "flexible", "evening"] = Field(
        default="flexible",
        description="Activity timing preference"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "userId": "user-123",
                "duration": "medium",
                "companions": "solo",
                "budget": "midrange",
                "pace": "balanced",
                "travelStyle": "cultural",
                "activity": "medium",
                "crowds": "mixed",
                "accommodation": "standard",
                "remote": False,
                "timing": "flexible"
            }
        }
