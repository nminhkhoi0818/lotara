"""
Tools module for Travel Lotara ADK Agents.

Provides function tools that agents can use:
- search_flights: Find flight options
- search_hotels: Find accommodation
- search_activities: Find things to do
- get_destination_information: Get destination info
- check_visa_requirements: Check travel requirements
- calculate_trip_budget: Budget calculations

Also includes:
- RAG engine for knowledge retrieval
- Calendar tool for date handling
"""

from travel_lotara.tools.travel_tools import (
    search_flights,
    search_hotels,
    search_activities,
    get_destination_information,
    check_visa_requirements,
    calculate_trip_budget,
)

from travel_lotara.tools.rag_engine import (
    RAGDocument,
    RAGQuery,
    RAGEngine,
)

__all__ = [
    # Core travel tools (used by ADK agents)
    "search_flights",
    "search_hotels",
    "search_activities",
    "get_destination_information",
    "check_visa_requirements",
    "calculate_trip_budget",
    # RAG components
    "RAGDocument",
    "RAGQuery",
    "RAGEngine",
]
