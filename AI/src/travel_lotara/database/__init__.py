"""
Database module for Travel Lotara.

Provides Supabase integration for persistent storage.
"""

from .client import get_supabase_client, SupabaseClient
from .repositories import (
    DestinationRepository,
    PreTripRepository,
    ItineraryRepository,
)
from .models import (
    JobRecord,
    SessionRecord,
    FeedbackRecord,
    UserPreferenceRecord,
    TravelItineraryRecord,
    JobStatus,
    WorkflowMode,
)

__all__ = [
    # Client
    "get_supabase_client",
    "SupabaseClient",
    # Repositories
    "DestinationRepository",
    "ItineraryRepository",
    "PreTripRepository",
    # Models
    "JobRecord",
    "SessionRecord",
    "FeedbackRecord",
    "UserPreferenceRecord",
    "TravelItineraryRecord",
    "JobStatus",
    "WorkflowMode",
]
