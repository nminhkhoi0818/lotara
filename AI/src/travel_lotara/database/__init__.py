"""
Database module for Travel Lotara.

Provides Supabase integration for persistent storage.
"""

from src.travel_lotara.database.client import get_supabase_client, SupabaseClient
from src.travel_lotara.database.repositories import (
    JobRepository,
    SessionRepository,
    FeedbackRepository,
    UserPreferenceRepository,
    ItineraryRepository,
)
from src.travel_lotara.database.models import (
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
    "JobRepository",
    "SessionRepository",
    "FeedbackRepository",
    "UserPreferenceRepository",
    "ItineraryRepository",
    # Models
    "JobRecord",
    "SessionRecord",
    "FeedbackRecord",
    "UserPreferenceRecord",
    "TravelItineraryRecord",
    "JobStatus",
    "WorkflowMode",
]
