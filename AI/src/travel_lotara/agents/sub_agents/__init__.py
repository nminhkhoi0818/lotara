from .inspiration_agent import *
from .pre_agent import *
from .planning_agent import (
    planning_agent,
    # Legacy singleton instances
    activities_retrieval_agent,
    attraction_retrieval_agent,
    hotel_retrieval_agent,
    # Factory functions for creating new instances
    create_attraction_retrieval_agent,
    create_hotel_retrieval_agent,
    create_activities_retrieval_agent,
)
from .formatter_agent import formatter_agent
from .planning_formatter_agent import planning_formatter_agent  # NEW merged agent

__all__ = [
    "pre_agent", 
    "inspiration_agent", 
    "planning_agent",
    "activities_retrieval_agent",
    "attraction_retrieval_agent",
    "hotel_retrieval_agent",
    "formatter_agent",
    "planning_formatter_agent",  # NEW merged agent
    "create_attraction_retrieval_agent",
    "create_hotel_retrieval_agent",
    "create_activities_retrieval_agent",
]