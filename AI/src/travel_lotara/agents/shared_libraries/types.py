
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Common data schema and types for travel-concierge agents."""

from typing import Annotated, Any, Optional, Union, List, Dict, Literal

from google.genai import types
from pydantic import BaseModel, Discriminator, Field

# Convenient declaration for controlled generation.
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json"
).model_dump()


##########################  PLANNING AGENT 

## Types for Transport Planner Agent Tool
class TransportSegment(BaseModel):
    from_city: str = Field(..., description="Departure city")
    to_city: str = Field(..., description="Arrival city")
    date: str = Field(..., description="Travel date (YYYY-MM-DD)")
    transport_mode: str = Field(..., description="Transport mode (flight, train, bus, car)")
    estimated_duration_hours: Optional[float] = Field(
        None, description="Estimated travel duration in hours"
    )
    cost_estimate_usd: Optional[float] = Field(
        None, description="Estimated cost in USD"
    )
    comfort_level: Optional[str] = Field(
        None, description="Comfort level (low, medium, high)"
    )
    notes: Optional[str] = Field(
        None, description="Reasoning or special considerations"
    )


class TransportPlan(BaseModel):
    transport_plan: list[TransportSegment] = Field(
        ..., description="List of transport segments for the trip"
    )

## Types for Itinerary Structuring Agent Tool
class DayPlan(BaseModel):
    day_number: int = Field(..., description="Sequential day number of the trip")
    date: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")
    location: str = Field(..., description="Primary location for the day")
    focus: str = Field(
        ..., description="Main focus (travel, exploration, relaxation)"
    )
    activities: list[str] = Field(
        ..., description="List of planned activities"
    )
    intensity: str = Field(
        ..., description="Activity intensity (low, medium, high)"
    )
    notes: Optional[str] = Field(
        None, description="Additional considerations or tips"
    )


class ItineraryStructurePlan(BaseModel):
    days: list[DayPlan] = Field(
        ..., description="Day-by-day structured itinerary"
    )

## Types for Accomodation Planner Agent Tool
class AccommodationStay(BaseModel):
    city: str = Field(..., description="City of accommodation")
    check_in_date: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out_date: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    accommodation_type: str = Field(
        ..., description="Accommodation type (hostel, hotel, boutique, resort)"
    )
    area: Optional[str] = Field(
        None, description="Recommended area or neighborhood"
    )
    budget_per_night: Optional[float] = Field(
        None, description="Estimated nightly budget"
    )
    notes: Optional[str] = Field(
        None, description="Special preferences or reasoning"
    )


class AccomodationPlan(BaseModel):
    stays: list[AccommodationStay] = Field(
        ..., description="Accommodation plan per destination"
    )


##########################  PRE-TRIP AGENT


class BudgetAndCostAwarenessPretrip(BaseModel):
    daily_spending_estimate: str = Field(
        ..., 
        description="Estimated daily cost range (e.g. $50–80/day)"
    )
    cost_breakdown: Dict[str, str] = Field(
        ..., 
        description="Cost categories with explanation (food, transport, activities)"
    )
    hidden_or_extra_costs: List[str] = Field(
        ..., 
        description="Common overlooked or surprise costs"
    )
    emergency_buffer_recommendation: str = Field(
        ..., 
        description="Suggested emergency fund amount or range"
    )
    payment_and_money_tips: List[str] = Field(
        ..., 
        description="Cash vs card, ATM access, currency notes"
    )

class PackingAndPrepPretrip(BaseModel):
    essentials: List[str] = Field(
        ..., 
        description="Must-have items for all travelers"
    )
    clothing: List[str] = Field(
        ..., 
        description="Weather- and activity-appropriate clothing"
    )
    electronics: List[str] = Field(
        ..., 
        description="Devices, chargers, adapters"
    )
    optional_or_special_items: Optional[List[str]] = Field(
        None, 
        description="Activity-specific or optional items"
    )
    preparation_tips: Optional[List[str]] = Field(
        None,
        description="Light preparation tips (offline maps, SIM, backups)"
    )


class ReadinessCheckPretrip(BaseModel):
    critical_checks: List[str] = Field(
        ..., 
        description="Must-confirm items before departure"
    )
    common_last_minute_mistakes: List[str] = Field(
        ..., 
        description="Typical traveler oversights"
    )
    readiness_status: str = Field(
        ..., 
        description="Short readiness assessment (e.g. 'You are well-prepared')"
    )
    final_reminder: Optional[str] = Field(
        None,
        description="Friendly closing reassurance"
    )



# =========================================================
########################## INSPIRATION AGENT
class DestinationDiscoveryPlan(BaseModel):
    regions: List[str] = Field(
        ..., 
        description="Vietnam regions to focus on (North, Central, South)"
    )
    recommended_destinations: List[str] = Field(
        ..., 
        description="List of cities/areas suitable for the user"
    )
    short_rationales: Dict[str, str] = Field(
        ..., 
        description="Mapping of destination -> 1 sentence justification"
    )


class ThemeAndStylePlan(BaseModel):
    traveler_persona: str = Field(
        ..., 
        description="Inferred traveler persona (e.g. foodie explorer, cultural traveler)"
    )
    recommended_themes: List[str] = Field(
        ..., 
        description="Travel themes (e.g. culinary, culture, nature, adventure)"
    )
    preferred_pace: str = Field(
        ..., 
        description="Preferred pace: slow / balanced / active"
    )
    experience_preferences: List[str] = Field(
        ..., 
        description="Experience style preferences (iconic vs hidden gems, social vs private)"
    )


class ConstraintAlignmentPlan(BaseModel):
    hard_constraints: Dict[str, str] = Field(
        ..., 
        description="Non-negotiable constraints (duration, budget tier, dates)"
    )
    soft_constraints: Dict[str, str] = Field(
        ..., 
        description="Flexible constraints (comfort, flexibility, crowd tolerance)"
    )
    detected_conflicts: List[str] = Field(
        ..., 
        description="Conflicts detected in user constraints"
    )
    recommended_limits: Dict[str, str] = Field(
        ..., 
        description="Safety limits (max cities, max regions, pacing limits)"
    )


# =========================================================
########################### USER PROFILE TYPE (ROOT INPUT)

class UserHomeLocation(BaseModel):
    city: str = Field(
        default="Ho Chi Minh City",
        description="Home city of the user"
    )
    country: str = Field(
        default="Vietnam",
        description="Home country of the user"
    )
    timezone: Optional[str] = Field(
        default="Asia/Ho_Chi_Minh",
        description="Home timezone of the user"
    )

class UserPreferences(BaseModel):        
    likes: List[str] = Field(..., description="User's likes")
    foods: List[str] = Field(..., description="User's food preferences")
    activities: List[str] = Field(..., description="User's activities")
    pace: str = Field(..., description="User's preferred travel pace")

class UserConstraints(BaseModel):
    mobility: List[str] = Field(..., description="User's mobility constraints")
    dietary: List[str] = Field(..., description="User's dietary constraints")
    time_limit_days: str = Field(..., description="User's time limit in days")
    dislikes: List[str] = Field(..., description="User's dislikes")
    allergies: List[str] = Field(..., description="User's allergies")

class UserProfile(BaseModel):
    travel_style: str = Field(..., description="User's preferred travel style")
    budget_range: str = Field(..., description="User's budget range")
    group_type: str = Field(..., description="User's group type")
    preferences: Optional[UserPreferences | Any] = Field(default=None, description="User's preferences")
    constraints: Optional[UserConstraints | Any] = Field(default=None, description="User's constraints")
    home_location: Optional[UserHomeLocation | Any] = Field(default=None, description="User's home location details")

# ########################### Itinerary TYPE (ROOT INPUT)

class LocationActivity(BaseModel):
    name: str = Field(description="Name of the location or activity")
    address: str = Field(description="Address of the location or activity")


class FlightEvents(BaseModel):
    event_type: Literal["flight"] = Field(description="Type of event, e.g., 'visit', 'activity', etc.")
    description: str = Field(description="Description of the flight event")
    departure_time: str = Field(description="Departure time of the flight event")
    arrival_time: str = Field(description="Arrival time of the flight event")
    budget: str = Field(description="Budget for the flight event")
    keywords: Optional[List[str]] = Field(description="Keywords related to the flight event")
    average_timespan: str = Field(description="Average timespan of the flight event")
    image_url: Optional[str] = Field(description="Image URL for the flight event")

class VisitEvents(BaseModel):
    event_type : Literal["visit"] = Field(
        description="Type of event, e.g., 'visit', 'activity', etc."
    )
    description: str = Field(description="Description of the visit event")
    start_time: str = Field(description="Start time of the visit event")
    end_time: str = Field(description="End time of the visit event")
    location: LocationActivity = Field(description="Location details of the visit event")
    budget: str = Field(description="Budget for the visit event")
    keywords: Optional[List[str]] = Field(description="Keywords related to the visit event")
    average_timespan: str = Field(description="Average timespan of the visit event")
    image_url: Optional[str] = Field(description="Image URL for the visit event")



class ActivityEvents(BaseModel):
    event_type : Literal["hotel_checkin"] | Literal["hotel_checkout"] = Field(
        description="Type of event, e.g., 'visit', 'activity', etc."
    )
    description: str = Field(description="Description of the visit event")
    location: LocationActivity = Field(description="Location details of the visit event")
    start_time: str = Field(description="Start time of the visit event")
    end_time: str = Field(description="End time of the visit event")
    budget: str = Field(description="Budget for the visit event")
    keywords: Optional[List[str]] = Field(description="Keywords related to the visit event")
    average_timespan: str = Field(description="Average timespan of the visit event")
    image_url: Optional[str] = Field(description="Image URL for the visit event")
class LocationActivity(BaseModel):
    name: str = Field(description="Name of the location")
    address: str = Field(description="Address of the location")


# Generic Event model that can represent any event type
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
    start_date: str = Field(description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(description="Trip end date (YYYY-MM-DD)")
    events: List[GenericEvent] = Field(
        description="List of events for the trip day."
    )

class Itinerary(BaseModel):
    trip_name: str = Field(description="Name of the trip")
    origin: str = Field(description="Trip origin location")
    destination: str = Field(description="Trip destination location")
    start_date: str = Field(description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(description="Trip end date (YYYY-MM-DD)")
    average_budget_spend_per_day: str = Field(description="Average daily budget (e.g., '$50 USD')")
    total_days: str = Field(description="Total number of days for the trip")
    average_ratings: str = Field(description="Average ratings of the trip")
    trip_overview: List[TripOverviewItinerary] = Field(
        description="Overview of the trip with daily summaries and events."
    )



# ########################### TRIP CONTEXT TYPE (ROOT INPUT)

class TripContextInput(BaseModel):
  userId: str = Field(..., description="Unique user identifier")
  duration: Optional[str] = Field(..., description="Trip duration category")
  companions: Optional[str] = Field(..., description="Type of travel companions")
  budget: Optional[str] = Field(..., description="Budget category")
  pace: Optional[str] = Field(..., description="Travel pace preference")
  travelStyle: Optional[str] = Field(..., description="Preferred travel style")
  activity: Optional[str] = Field(..., description="Activity level preference")
  crowds: Optional[str] = Field(..., description="Crowd preference")
  accommodation: Optional[str] = Field(..., description="Accommodation standard")
  remote: Optional[bool] = Field(..., description="Remote work required")
  timing: Optional[str] = Field(..., description="Timing flexibility")


# ########################### OUTPUT MESSAGE TYPE (ROOT OUTPUT)

class AnswerFormat(BaseModel):
    location_name: str = Field(..., description="Name of the location suggested")
    description: str = Field(..., description="Description of the location suggested")
    rating: float = Field(..., description="Rating of the location suggested")
    total_days: int = Field(..., description="Total days recommended for the location")
    average_budget_spend_per_day: float = Field(..., description="Average cost per day in USD for the location")
    image_url: Optional[str] = Field(None, description="Image URL representing the location suggested")
    key_words: List[str] = Field(..., description="List of keywords associated with the location suggested")
    trip_overview: List[TripOverviewItinerary] = Field(
        description="Overview of the trip with daily summaries and events"
    )


class OutputMessage(BaseModel):
    answers: AnswerFormat = Field(
        ..., 
        description="Output message from the agent with location details"
    )


class TravelConcept(BaseModel):
    concept_name: str = Field(..., description="Name of the travel concept")
    core_vibe: str = Field(..., description="Core vibe of the travel concept")
    primary_interests: List[str] = Field(..., description="Primary interests for this concept")
    signature_experiences: List[str] = Field(..., description="Signature experiences")
    pace_style: str = Field(..., description="Pace style for this concept")

class PlanningConstraints(BaseModel):
    preferred_pace: str = Field(..., description="Preferred travel pace")
    crowd_tolerance: str = Field(..., description="Tolerance for crowds")
    experience_density: str = Field(..., description="Density of experiences")
    transition_tolerance: str = Field(..., description="Tolerance for transitions")

class Inpsiration_Output(BaseModel):
    traveler_persona: str = Field(..., description="Inferred traveler persona")
    recommended_regions: list[str] = Field(..., description="Recommended regions to visit")
    travel_concepts: List[TravelConcept] = Field(
        ..., 
        description="List of travel concepts with details"
    )
    planning_constraints: PlanningConstraints = Field(
        ..., 
        description="Planning constraints for the trip"
    )