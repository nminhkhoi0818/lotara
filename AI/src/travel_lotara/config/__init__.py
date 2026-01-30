"""
Configuration module for Travel Lotara.

Usage:
    from travel_lotara.config import get_settings, Settings
    
    settings = get_settings()
    print(settings.model)  # gemini/gemini-2.0-flash
"""

from .settings import (
    Settings,
    load_settings,
    get_settings,
)

__all__ = [
    "Settings",
    "load_settings",
    "get_settings",
]
