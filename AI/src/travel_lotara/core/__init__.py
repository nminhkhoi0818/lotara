"""
Core module for Travel Lotara.

Provides:
- State management for session and persistent memory
- Parser utilities for structured data extraction
- Evaluation tools for agent quality assessment
"""

from src.travel_lotara.core.state_manager import (
    SessionState,
    SessionStateManager,
    PersistentMemoryItem,
    PersistentMemoryStore,
)

from .input_parser import (
    parse_backend_input, 
    create_natural_language_query
)

__all__ = [
    # State management
    "SessionState",
    "SessionStateManager",
    "PersistentMemoryItem",
    "PersistentMemoryStore",
    # Input parsing
    "parse_backend_input",
    "create_natural_language_query",
]
