from typing import List, Optional
from pydantic import BaseModel, Field


class Place(BaseModel):
    name: str
    budget: str
    time: Optional[str] = None
    average_timespan: Optional[str] = None


class Cuisine(BaseModel):
    name: str
    budget: str
    average_timespan: Optional[str] = None


class Destinations(BaseModel):
    places: List[Place]
    cuisines: List[Cuisine]


class Hotel(BaseModel):
    name: str
    cost: str
    reviews: Optional[str] = None


class TravelFinalResponse(BaseModel):
    index: int = Field(..., ge=1)
    location_name: str
    location: str
    description: str
    rating: float = Field(..., ge=0, le=5)
    total_days: str
    average_budget_spend_per_day: str
    image: str
    keywords: List[str]
    destinations: Destinations
    hotels: List[Hotel]
