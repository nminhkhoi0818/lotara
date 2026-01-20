"""
Travel Lotara - AI Travel Planning Assistant

Multi-agent system built with Google ADK for comprehensive travel planning.
All agents are traced with Opik for full observability.

Quick Start:
    # Using ADK CLI
    adk run travel_lotara.agent
    adk web travel_lotara.agent
    
    # Using Python
    from travel_lotara.agent import root_agent
    from travel_lotara.tools import search_flights, search_hotels
    from travel_lotara.guardrails import apply_guardrails_to_agent
    from travel_lotara.config import get_settings

Project Structure:
    - agent.py: ADK agents with Opik tracing
    - tools/: Function tools for agents  
    - guardrails/: Input/output validation callbacks
    - config/: Settings and configuration
    - core/: State management and utilities
    - tracking/: Opik tracing exports
    - data/: Fixture data for development
"""

__version__ = "0.1.0"

# Convenience imports
from travel_lotara.config import get_settings, Settings
