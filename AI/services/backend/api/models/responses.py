"""Response models for the API."""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class LocationActivity(BaseModel):
    """Location model for events."""
    name: str = Field(description="Name of the location")
    address: str = Field(description="Address of the location")


class GenericEvent(BaseModel):
    event_type: str = Field(description="Type of event: flight, visit, hotel_checkin, hotel_checkout, etc.")
    description: str = Field(description="Description of the event")
    start_time: Optional[str] = Field(None, description="Start time of the event")
    end_time: Optional[str] = Field(None, description="End time of the event")
    departure_time: Optional[str] = Field(None, description="Departure time (for flights)")
    arrival_time: Optional[str] = Field(None, description="Arrival time (for flights)")
    location: Optional[LocationActivity] = Field(None, description="Location details")
    budget: Optional[str] = Field(None, description="Budget for the event")
    keywords: Optional[List[str]] = Field(None, description="Keywords related to the event")
    average_timespan: Optional[str] = Field(None, description="Average duration of the event")
    image_url: Optional[str] = Field(None, description="Image URL for the event")


class TripOverviewItinerary(BaseModel):
    trip_number: int = Field(description="Sequential trip number")
    summary: str = Field(description="Brief summary of the trip")
    events: List[GenericEvent] = Field(
        description="List of events for the trip day."
    )

class Itinerary(BaseModel):
    trip_name: str = Field(description="Name of the trip")
    origin: str = Field(description="Trip origin location")
    destination: str = Field(description="Trip destination location")
    total_days: str = Field(description="Total number of days for the trip")
    average_budget_spend_per_day: str = Field(description="Average daily budget (e.g., '$50 USD')")
    average_ratings: str = Field(description="Average ratings of the trip")
    trip_overview: List[TripOverviewItinerary] = Field(
        description="Overview of the trip with daily summaries and events."
    )
class ItineraryResponse(BaseModel):
    """Response model for itinerary generation."""
    
    status: str = Field(..., description="Request status: pending, processing, completed, failed")
    session_id: str = Field(..., description="Session ID for tracking")
    user_id: str = Field(..., description="User ID")
    itinerary: Optional[Itinerary] = Field(None, description="Generated itinerary data")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "session_id": "sess_abc123",
                "user_id": "user-123",
                "itinerary": {
                "trip_name": "Summer Trip to Tokyo",
                "origin": "Ho Chi Minh City, Vietnam",
                "destination": "Tokyo, Japan",    
                "average_budget_spend_per_day": "400 USD",
                "total_days": "2",
                "average_ratings": "4.8",
                "trip_overview": [
                    {
                    "trip_number": 1,
                    "summary": "Arrival in Tokyo, hotel check-in, visit Senso-ji Temple and Tokyo Tower.",
                    "events": [
                        {
                        "event_type": "flight",
                        "description": "Flight from Ho Chi Minh City to Tokyo",
                        "departure_time": "08:00 AM UTC+7",
                        "arrival_time": "02:00 PM UTC+9",
                        "budget": "300 USD",
                        "keywords": ["flight", "Ho Chi Minh City", "Tokyo"],
                        "average_timespan": "6 hours",
                        "image_url": ""
                        },
                        {
                        "event_type": "hotel_checkin",
                        "description": "Check-in at Tokyo Central Hotel",
                        "location": {
                            "name": "Tokyo Central Hotel",
                            "address": "1-1-1 Shinjuku, Tokyo, Japan"
                        },
                        "start_time": "03:00 PM UTC+9",
                        "end_time": "03:30 PM UTC+9",
                        "budget": "150 USD per night",
                        "keywords": ["hotel", "Tokyo Central Hotel", "check-in", "Tokyo"],
                        "average_timespan": "30 minutes",
                        "image_url": ""
                        },
                        {
                        "event_type": "visit",
                        "description": "Visit to Senso-ji Temple",
                        "start_time": "07:00 PM UTC+9",
                        "end_time": "08:30 PM UTC+9",
                        "budget": "50 USD",
                        "keywords": ["visit", "Senso-ji Temple", "Tokyo"],
                        "average_timespan": "1.5 hours",
                        "image_url": ""
                        },
                        {
                        "event_type": "visit",
                        "description": "Visit to Tokyo Tower",
                        "start_time": "09:00 PM UTC+9",
                        "end_time": "10:30 PM UTC+9",
                        "budget": "50 USD",
                        "keywords": ["visit", "Tokyo Tower", "Tokyo"],
                        "average_timespan": "1.5 hours",
                        "image_url": ""
                        }
                    ]
                    },
                    {
                    "trip_number": 2,
                    "summary": "Visit to Meiji Shrine, hotel check-out, flight back to Ho Chi Minh City.",
                    "events": [
                        {
                        "event_type": "visit",
                        "description": "Visit to Meiji Shrine",
                        "start_time": "09:00 AM UTC+9",
                        "end_time": "11:00 AM UTC+9",
                        "location": {
                            "name": "Meiji Shrine",
                            "address": "1-1 Yoyogikamizonocho, Shibuya City, Tokyo, Japan"
                        },
                        "budget": "58 USD",
                        "keywords": ["visit", "Meiji Shrine", "Tokyo"],
                        "average_timespan": "2 hours",
                        "image_url": ""
                        },
                        {
                        "event_type": "hotel_checkout",
                        "description": "Check-out from Tokyo Central Hotel",
                        "location": {
                            "name": "Tokyo Central Hotel",
                            "address": "1-1-1 Shinjuku, Tokyo, Japan"
                        },
                        "start_time": "11:00 AM UTC+9",
                        "end_time": "11:30 AM UTC+9",
                        "budget": "0 USD",
                        "keywords": ["hotel", "Tokyo Central Hotel", "check-out", "Tokyo"],
                        "average_timespan": "30 minutes",
                        "image_url": ""
                        },
                        {
                        "event_type": "flight",
                        "description": "Flight from Tokyo to Ho Chi Minh City",
                        "departure_time": "02:00 PM UTC+9",
                        "arrival_time": "06:00 PM UTC+7",
                        "budget": "300 USD",
                        "keywords": ["flight", "Tokyo", "Ho Chi Minh City"],
                        "average_timespan": "6 hours",
                        "image_url": ""
                        }
                    ]
                    }
                ]
                },
                "error": "null",
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
