# """
# Travel Tools for Google ADK Agents

# Function tools that ADK agents can use for travel planning.
# Tools are simple functions with docstrings that ADK auto-wraps.
# """

# from __future__ import annotations

# from typing import Any
# from src.travel_lotara.data.fixtures import (
#     get_flight_fixtures,
#     get_hotel_fixtures,
#     get_activity_fixtures,
#     get_destination_info,
# )


# # ============================================
# # FLIGHT TOOLS
# # ============================================

# def search_flights(
#     origin: str,
#     destination: str,
#     depart_date: str,
#     return_date: str | None = None,
#     max_price_usd: float | None = None,
# ) -> dict[str, Any]:
#     """
#     Search for available flights between two cities.
    
#     Args:
#         origin: Departure city or airport code (e.g., 'NYC', 'LAX')
#         destination: Arrival city or airport code (e.g., 'PAR', 'LON')
#         depart_date: Departure date in YYYY-MM-DD format
#         return_date: Optional return date in YYYY-MM-DD format for round trips
#         max_price_usd: Optional maximum price filter in USD
        
#     Returns:
#         dict: Contains 'status', 'flights' list, and 'sources'
#     """
#     try:
#         flights = get_flight_fixtures(origin, destination)
        
#         # Filter by price if specified
#         if max_price_usd:
#             flights = [f for f in flights if f.get("price_usd", 0) <= max_price_usd]
        
#         # Sort by price (best deals first)
#         flights = sorted(flights, key=lambda x: x.get("price_usd", 0))
        
#         return {
#             "status": "success",
#             "flights": flights[:10],  # Return top 10
#             "total_found": len(flights),
#             "sources": ["amadeus_api", "skyscanner", "google_flights"],
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": f"Failed to search flights: {str(e)}",
#         }


# # ============================================
# # HOTEL TOOLS
# # ============================================

# def search_hotels(
#     destination: str,
#     check_in: str,
#     check_out: str,
#     max_price_per_night_usd: float | None = None,
#     min_rating: float | None = None,
# ) -> dict[str, Any]:
#     """
#     Search for available hotels in a destination.
    
#     Args:
#         destination: City name (e.g., 'Paris', 'Tokyo')
#         check_in: Check-in date in YYYY-MM-DD format
#         check_out: Check-out date in YYYY-MM-DD format
#         max_price_per_night_usd: Optional maximum price per night in USD
#         min_rating: Optional minimum rating (0.0-5.0)
        
#     Returns:
#         dict: Contains 'status', 'hotels' list, and 'sources'
#     """
#     try:
#         hotels = get_hotel_fixtures(destination)
        
#         # Filter by price if specified
#         if max_price_per_night_usd:
#             hotels = [h for h in hotels if h.get("price_per_night_usd", 0) <= max_price_per_night_usd]
        
#         # Filter by rating if specified
#         if min_rating:
#             hotels = [h for h in hotels if h.get("rating", 0) >= min_rating]
        
#         # Sort by rating (best first)
#         hotels = sorted(hotels, key=lambda x: x.get("rating", 0), reverse=True)
        
#         return {
#             "status": "success",
#             "hotels": hotels[:10],  # Return top 10
#             "total_found": len(hotels),
#             "sources": ["booking.com", "hotels.com", "expedia"],
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": f"Failed to search hotels: {str(e)}",
#         }


# # ============================================
# # ACTIVITY TOOLS
# # ============================================

# def search_activities(
#     destination: str,
#     interests: str | None = None,
#     max_price_usd: float | None = None,
# ) -> dict[str, Any]:
#     """
#     Search for activities and attractions in a destination.
    
#     Args:
#         destination: City name (e.g., 'Paris', 'Tokyo')
#         interests: Comma-separated interests (e.g., 'museums, food, art')
#         max_price_usd: Optional maximum price filter in USD
        
#     Returns:
#         dict: Contains 'status', 'activities' list, and 'sources'
#     """
#     try:
#         activities = get_activity_fixtures(destination)
        
#         # Parse interests
#         interest_list = [i.strip().lower() for i in (interests or "").split(",") if i.strip()]
        
#         # Filter by interests if specified
#         if interest_list:
#             filtered = []
#             for activity in activities:
#                 category_lower = activity.get("category", "").lower()
#                 desc_lower = activity.get("description", "").lower()
#                 name_lower = activity.get("name", "").lower()
                
#                 for interest in interest_list:
#                     if interest in category_lower or interest in desc_lower or interest in name_lower:
#                         filtered.append(activity)
#                         break
            
#             activities = filtered if filtered else activities
        
#         # Filter by price if specified
#         if max_price_usd:
#             activities = [a for a in activities if a.get("price_usd", 0) <= max_price_usd]
        
#         # Sort by rating
#         activities = sorted(activities, key=lambda x: x.get("rating", 0), reverse=True)
        
#         return {
#             "status": "success",
#             "activities": activities[:15],  # Return top 15
#             "total_found": len(activities),
#             "sources": ["viator", "getyourguide", "tripadvisor"],
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": f"Failed to search activities: {str(e)}",
#         }


# # ============================================
# # DESTINATION INFO TOOLS
# # ============================================

# def get_destination_information(destination: str) -> dict[str, Any]:
#     """
#     Get general information about a travel destination.
    
#     Args:
#         destination: City or country name (e.g., 'Paris', 'Japan')
        
#     Returns:
#         dict: Contains destination info including weather, currency, language, tips
#     """
#     try:
#         info = get_destination_info(destination)
        
#         return {
#             "status": "success",
#             "destination": destination,
#             "info": info,
#             "sources": ["wikitravel", "lonelyplanet", "tripadvisor"],
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": f"Failed to get destination info: {str(e)}",
#         }


# # ============================================
# # VISA / TRAVEL REQUIREMENTS TOOLS  
# # ============================================

# def check_visa_requirements(
#     citizenship: str,
#     destination: str,
# ) -> dict[str, Any]:
#     """
#     Check visa requirements for traveling to a destination.
    
#     Args:
#         citizenship: Country of citizenship (e.g., 'USA', 'United Kingdom')
#         destination: Destination country (e.g., 'France', 'Japan')
        
#     Returns:
#         dict: Contains visa requirement information
#     """
#     # Simplified visa check - in production, use official API
#     visa_free_combinations = {
#         ("USA", "France"): True,
#         ("USA", "Japan"): True,
#         ("USA", "United Kingdom"): True,
#         ("United Kingdom", "France"): True,
#         ("United Kingdom", "Japan"): True,
#     }
    
#     key = (citizenship.upper() if len(citizenship) <= 3 else citizenship.title(), 
#            destination.title())
    
#     is_visa_free = visa_free_combinations.get(key, None)
    
#     if is_visa_free is True:
#         return {
#             "status": "success",
#             "requires_visa": False,
#             "max_stay_days": 90,
#             "notes": "Visa-free travel for tourism up to 90 days",
#             "confidence": 0.9,
#             "sources": ["timaticweb", "embassy_info"],
#         }
#     elif is_visa_free is False:
#         return {
#             "status": "success",
#             "requires_visa": True,
#             "visa_type": "Tourist Visa",
#             "notes": "Visa required. Apply at embassy or consulate.",
#             "confidence": 0.9,
#             "sources": ["timaticweb", "embassy_info"],
#         }
#     else:
#         return {
#             "status": "requires_verification",
#             "requires_visa": "unknown",
#             "notes": "Please verify with official embassy or consulate",
#             "confidence": 0.3,
#             "sources": [],
#         }


# # ============================================
# # BUDGET CALCULATION TOOLS
# # ============================================

# def calculate_trip_budget(
#     flight_cost: float,
#     hotel_cost_per_night: float,
#     num_nights: int,
#     daily_activities_budget: float = 100.0,
#     daily_food_budget: float = 75.0,
#     miscellaneous_budget: float = 200.0,
# ) -> dict[str, Any]:
#     """
#     Calculate estimated total trip budget.
    
#     Args:
#         flight_cost: Total flight cost in USD
#         hotel_cost_per_night: Hotel cost per night in USD
#         num_nights: Number of nights staying
#         daily_activities_budget: Daily budget for activities in USD
#         daily_food_budget: Daily budget for food in USD
#         miscellaneous_budget: Buffer for miscellaneous expenses in USD
        
#     Returns:
#         dict: Contains itemized budget breakdown and total
#     """
#     try:
#         hotel_total = hotel_cost_per_night * num_nights
#         activities_total = daily_activities_budget * num_nights
#         food_total = daily_food_budget * num_nights
        
#         total = flight_cost + hotel_total + activities_total + food_total + miscellaneous_budget
        
#         return {
#             "status": "success",
#             "breakdown": {
#                 "flights": flight_cost,
#                 "accommodation": hotel_total,
#                 "activities": activities_total,
#                 "food_and_dining": food_total,
#                 "miscellaneous": miscellaneous_budget,
#             },
#             "total_estimated_cost_usd": total,
#             "num_nights": num_nights,
#             "daily_average": total / max(num_nights, 1),
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": f"Failed to calculate budget: {str(e)}",
#         }
