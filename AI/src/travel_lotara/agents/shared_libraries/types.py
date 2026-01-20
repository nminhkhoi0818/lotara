
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

from typing import Optional, Union, List, Dict

from google.genai import types
from pydantic import BaseModel, Field

# Convenient declaration for controlled generation.
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json"
)


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
    comfort_level: Optional[str] = Field(
        None, description="Comfort level (low, medium, high)"
    )
    notes: Optional[str] = Field(
        None, description="Reasoning or special considerations"
    )


class TransportPlan(BaseModel):
    segments: list[TransportSegment] = Field(
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


class UserProfile(BaseModel):
    name: Optional[str]
    travel_companions: str = Field(
        ..., description="solo / couple / family / friends"
    )
    budget_tier: str = Field(
        ..., description="budget / mid-range / luxury"
    )
    trip_duration_days: int
    travel_pace: Optional[str] = Field(
        None, description="slow / balanced / active"
    )
    interests: List[str] = Field(
        ..., description="food, culture, nature, beach, nightlife, adventure"
    )
    crowd_preference: Optional[str] = Field(
        None, description="avoid crowds / neutral / love crowds"
    )
    remote_work_required: Optional[bool] = False
    flexibility_level: Optional[str] = Field(
        None, description="low / medium / high"
    )

