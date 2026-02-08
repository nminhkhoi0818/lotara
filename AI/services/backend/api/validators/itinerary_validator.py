"""Itinerary validation and retry logic."""

import json
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ValidationError


# Define schema locally to avoid circular dependencies
class LocationActivity(BaseModel):
    """Location model for events."""
    name: str
    address: str


class GenericEvent(BaseModel):
    """Generic event model."""
    event_type: str
    description: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    location: Optional[LocationActivity] = None
    location_name: Optional[str] = None
    budget: Optional[str] = None
    keywords: Optional[List[str]] = None
    average_timespan: Optional[str] = None
    image_url: Optional[str] = None


class TripOverviewItinerary(BaseModel):
    """Trip overview model."""
    trip_number: int
    summary: str
    events: List[GenericEvent]


class Itinerary(BaseModel):
    """Itinerary model for validation."""
    trip_name: str
    origin: str
    destination: str
    total_days: str
    average_budget_spend_per_day: str
    average_ratings: str
    trip_overview: List[TripOverviewItinerary]


class ItineraryValidationResult(BaseModel):
    """Result of itinerary validation."""
    is_valid: bool
    itinerary: Optional[Dict[str, Any]] = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def validate_itinerary_structure(data: Any) -> ItineraryValidationResult:
    """
    Validate that the itinerary matches the expected schema.
    
    Args:
        data: Raw itinerary data (dict, str, or any JSON-serializable type)
        
    Returns:
        ItineraryValidationResult with validation status and any errors
    """
    errors = []
    warnings = []
    
    # Handle string input (try to parse as JSON)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return ItineraryValidationResult(
                is_valid=False,
                errors=[f"Invalid JSON: {str(e)}"]
            )
    
    # Ensure we have a dict
    if not isinstance(data, dict):
        return ItineraryValidationResult(
            is_valid=False,
            errors=[f"Expected dict, got {type(data).__name__}"]
        )
    
    # Validate against Pydantic schema
    try:
        validated_itinerary = Itinerary(**data)
        itinerary_dict = validated_itinerary.model_dump()
        
        # Additional custom validations
        _validate_events(itinerary_dict, errors, warnings)
        _validate_completeness(itinerary_dict, errors, warnings)
        
        return ItineraryValidationResult(
            is_valid=len(errors) == 0,
            itinerary=itinerary_dict,
            errors=errors,
            warnings=warnings
        )
        
    except ValidationError as e:
        # Extract validation errors
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            msg = error["msg"]
            errors.append(f"Field '{field}': {msg}")
        
        return ItineraryValidationResult(
            is_valid=False,
            itinerary=data,  # Return original data
            errors=errors
        )
    except Exception as e:
        return ItineraryValidationResult(
            is_valid=False,
            errors=[f"Validation error: {str(e)}"]
        )



def _validate_events(itinerary: Dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    """Validate events in trip overview."""
    trip_overview = itinerary.get("trip_overview", [])
    
    if not trip_overview:
        errors.append("trip_overview is empty - no events found")
        return
    
    for idx, trip in enumerate(trip_overview):
        if not isinstance(trip, dict):
            errors.append(f"trip_overview[{idx}] is not a dict")
            continue
            
        events = trip.get("events", [])
        if not events:
            warnings.append(f"Trip {idx+1} has no events")
            continue
        
        # Check event structure
        for event_idx, event in enumerate(events):
            if not isinstance(event, dict):
                errors.append(f"Trip {idx+1}, event {event_idx+1} is not a dict")
                continue
            
            # Validate required event fields
            if "event_type" not in event:
                errors.append(f"Trip {idx+1}, event {event_idx+1} missing event_type")
            if "description" not in event:
                errors.append(f"Trip {idx+1}, event {event_idx+1} missing description")


def _validate_completeness(itinerary: Dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    """Validate completeness of itinerary data."""
    required_fields = [
        "trip_name", "origin", "destination", "total_days", 
        "average_budget_spend_per_day", "average_ratings", "trip_overview"
    ]
    
    for field in required_fields:
        if field not in itinerary or itinerary[field] is None:
            errors.append(f"Missing required field: {field}")
        elif isinstance(itinerary[field], str) and not itinerary[field].strip():
            warnings.append(f"Field '{field}' is empty")


def normalize_itinerary_output(raw_data: Any) -> Dict[str, Any]:
    """
    Normalize various output formats to match expected structure.
    
    Handles cases where:
    - Agent returns nested structure
    - Agent returns text that needs parsing
    - Field names don't match exactly
    
    Args:
        raw_data: Raw output from agent
        
    Returns:
        Normalized dictionary matching expected schema
    """
    if isinstance(raw_data, str):
        try:
            raw_data = json.loads(raw_data)
        except json.JSONDecodeError:
            # Return minimal structure if can't parse
            return {
                "trip_name": "Untitled Trip",
                "origin": "Unknown",
                "destination": "Unknown",
                "total_days": "0",
                "average_budget_spend_per_day": "$50 USD",
                "average_ratings": "0.0",
                "trip_overview": [],
                "raw_response": raw_data
            }
    
    if not isinstance(raw_data, dict):
        return {
            "trip_name": "Error",
            "origin": "Unknown",
            "destination": "Unknown",
            "total_days": "0",
            "average_budget_spend_per_day": "$50 USD",
            "average_ratings": "0.0",
            "trip_overview": [],
            "error": f"Invalid data type: {type(raw_data)}"
        }
    
    # Handle nested structures (e.g., {answers: {actual_data}})
    if "answers" in raw_data and isinstance(raw_data["answers"], dict):
        raw_data = raw_data["answers"]
    
    # Ensure all required fields exist
    normalized = {
        "trip_name": raw_data.get("trip_name", raw_data.get("location_name", "Untitled Trip")),
        "origin": raw_data.get("origin", "Unknown"),
        "destination": raw_data.get("destination", raw_data.get("location_name", "Unknown")),
        "total_days": str(raw_data.get("total_days", 0)),
        "average_budget_spend_per_day": raw_data.get("average_budget_spend_per_day", "$50 USD"),
        "average_ratings": str(raw_data.get("average_ratings", raw_data.get("rating", "0.0"))),
        "trip_overview": raw_data.get("trip_overview", []),
    }
    
    return normalized
