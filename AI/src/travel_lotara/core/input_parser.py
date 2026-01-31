"""
Input parser to convert backend JSON to agent-compatible format.

Backend sends:
{
  "userId": "uuid",
  "duration": "medium",
  "companions": "solo",
  "budget": "midrange",
  "pace": "balanced",
  "travelStyle": "cultural",
  "activity": "medium",
  "crowds": "mixed",
  "accommodation": "standard",
  "remote": false,
  "timing": "flexible"
}

Agent expects user_profile in state.
"""

from typing import Dict, Any
from datetime import datetime, timedelta


# Mapping from backend values to agent-friendly descriptions
DURATION_MAP = {
    "short": {"days": 5, "label": "3-5 days"},
    "medium": {"days": 10, "label": "1-2 weeks"},
    "long": {"days": 21, "label": "2-4 weeks"},
    "extended": {"days": 35, "label": "1 month+"}
}

BUDGET_MAP = {
    "budget": {"daily": "$20-50", "range": "budget"},
    "midrange": {"daily": "$50-100", "range": "mid-range"},
    "comfortable": {"daily": "$100-200", "range": "comfortable"},
    "luxury": {"daily": "$200+", "range": "luxury"}
}

COMPANIONS_MAP = {
    "solo": "solo traveler",
    "couple": "couple",
    "family_kids": "family with young children",
    "family_adults": "family (adults only)",
    "friends": "friends group"
}

TRAVEL_STYLE_MAP = {
    "adventure": {"primary": "adventure & outdoor activities", "activities": ["hiking", "trekking", "water sports"]},
    "cultural": {"primary": "culture & history immersion", "activities": ["museum visits", "temple tours", "local experiences"]},
    "nature": {"primary": "nature, beaches & scenic beauty", "activities": ["beach relaxation", "national parks", "scenic views"]},
    "food": {"primary": "food & culinary experiences", "activities": ["cooking classes", "food tours", "local markets"]},
    "wellness": {"primary": "relaxation & wellness", "activities": ["spa", "yoga", "meditation"]},
    "photography": {"primary": "photography & Instagram-worthy spots", "activities": ["sunrise photography", "iconic landmarks", "hidden gems"]}
}

ACTIVITY_LEVEL_MAP = {
    "low": "relaxed pace - minimal walking",
    "medium": "moderately active - comfortable walking & light activities",
    "high": "very active - hiking, biking, full-day adventures"
}

CROWDS_MAP = {
    "avoid": "avoid crowds - prefer hidden gems & local spots",
    "mixed": "mix of both - main sights + off-beaten-path",
    "embrace": "embrace crowds - don't miss the iconic spots"
}

ACCOMMODATION_MAP = {
    "hostel": "hostels & guesthouses",
    "standard": "standard hotels",
    "boutique": "boutique hotels",
    "premium": "luxury resorts & 5-star hotels"
}

TIMING_MAP = {
    "morning": "early mornings - sunrise adventures",
    "flexible": "flexible - spread throughout the day",
    "evening": "late start - afternoons & evenings"
}


def parse_backend_input(backend_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert backend JSON to agent state format.
    
    Args:
        backend_data: JSON from backend with user preferences
    
    Returns:
        Agent-compatible state dictionary
    """
    # Extract values
    duration_key = backend_data.get("duration", "medium")
    companions_key = backend_data.get("companions", "solo")
    budget_key = backend_data.get("budget", "midrange")
    style_key = backend_data.get("travelStyle", "cultural")
    activity_key = backend_data.get("activity", "medium")
    crowds_key = backend_data.get("crowds", "mixed")
    accommodation_key = backend_data.get("accommodation", "standard")
    pace_key = backend_data.get("pace", "balanced")
    timing_key = backend_data.get("timing", "flexible")
    remote = backend_data.get("remote", False)
    
    # Calculate dates (default to 2 weeks from now)
    start_date = datetime.now() + timedelta(days=14)
    duration_days = DURATION_MAP.get(duration_key, DURATION_MAP["medium"])["days"]
    end_date = start_date + timedelta(days=duration_days)
    
    # Map to agent state format
    travel_style_info = TRAVEL_STYLE_MAP.get(style_key, TRAVEL_STYLE_MAP["cultural"])
    budget_info = BUDGET_MAP.get(budget_key, BUDGET_MAP["midrange"])
    
    state = {
        "user_profile": {
            "travel_style": travel_style_info["primary"],
            "budget_range": budget_info["daily"],
            "group_type": COMPANIONS_MAP.get(companions_key, "solo traveler"),
            "preferences": {
                "likes": travel_style_info["activities"],
                "foods": [],  # Will be inferred by agent
                "activities": travel_style_info["activities"],
                "pace": pace_key,
                "activity_level": ACTIVITY_LEVEL_MAP.get(activity_key, "moderately active"),
                "crowd_preference": CROWDS_MAP.get(crowds_key, "mix of both"),
                "timing_preference": TIMING_MAP.get(timing_key, "flexible"),
                "accommodation_type": ACCOMMODATION_MAP.get(accommodation_key, "standard hotels"),
                "remote_work": remote
            },
            "constraints": {
                "mobility": [],
                "dietary": [],
                "time_limit_days": str(duration_days),
                "dislikes": [],
                "allergies": []
            },
            "home_location": {
                "event_type": "home",
                "city": "Ho Chi Minh City",  # Default, can be overridden
                "country": "Vietnam",
                "timezone": "Asia/Ho_Chi_Minh"
            }
        },
        "itinerary": {
            "trip_name": "",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "origin": "Ho Chi Minh City, Vietnam",
            "destination": "Vietnam",  # Will be refined by inspiration agent
            "total_days": str(duration_days),
            "average_ratings": "",
            "trip_overview": []
        },
        "origin": "Ho Chi Minh City, Vietnam",
        "destination": "Vietnam",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "itinerary_start_date": start_date.strftime("%Y-%m-%d"),
        "itinerary_end_date": end_date.strftime("%Y-%m-%d"),
        "total_days": duration_days,
        "average_budget_spend_per_day": budget_info["daily"],
        "average_ratings": ""
    }
    
    return state


def create_natural_language_query(backend_data: Dict[str, Any]) -> str:
    """
    Convert backend JSON to natural language query for the agent.
    
    This creates a human-readable request that the agent can process.
    """
    duration_key = backend_data.get("duration", "medium")
    companions_key = backend_data.get("companions", "solo")
    budget_key = backend_data.get("budget", "midrange")
    style_key = backend_data.get("travelStyle", "cultural")
    pace_key = backend_data.get("pace", "balanced")
    
    duration_label = DURATION_MAP.get(duration_key, DURATION_MAP["medium"])["label"]
    companion_label = COMPANIONS_MAP.get(companions_key, "solo traveler")
    budget_label = BUDGET_MAP.get(budget_key, BUDGET_MAP["midrange"])["daily"]
    style_label = TRAVEL_STYLE_MAP.get(style_key, TRAVEL_STYLE_MAP["cultural"])["primary"]
    
    # Calculate dates
    start_date = datetime.now() + timedelta(days=14)
    duration_days = DURATION_MAP.get(duration_key, DURATION_MAP["medium"])["days"]
    end_date = start_date + timedelta(days=duration_days)
    
    query = (
        f"I need a detailed day-by-day travel plan for Vietnam. "
        f"Duration: {duration_label} ({duration_days} days) from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}. "
        f"Traveler: {companion_label}, Style: {style_label}, Budget: {budget_label}/day, Pace: {pace_key}. "
        f"Please create a complete detailed itinerary with transport, accommodation, and daily activities."
    )
    
    return query
