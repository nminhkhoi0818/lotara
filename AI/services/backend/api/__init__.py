"""
Travel Lotara AI - API Package

This package contains the FastAPI application for Vercel deployment.
"""

from .models import (
    PlanRequest,
    SuggestRequest,
    ApprovalRequest,
    FeedbackRequest,
    JobResponse,
    JobStatusResponse,
    HealthResponse,
    ErrorResponse,
    JobStatus,
    WorkflowMode,
    EventType,
    StreamEvent,
    JobState,
    TaskInfo,
)

# Export app for Vercel - this is the main entry point
from .app import app

# Export orchestrators
from .orchestrator import (
    TravelOrchestrator,
    SuggestionOrchestrator,
    get_travel_orchestrator,
    get_suggestion_orchestrator,
)

__all__ = [
    # FastAPI app
    "app",
    # Orchestrators
    "TravelOrchestrator",
    "SuggestionOrchestrator",
    "get_travel_orchestrator",
    "get_suggestion_orchestrator",
    # Request models
    "PlanRequest",
    "SuggestRequest",
    "ApprovalRequest",
    "FeedbackRequest",
    # Response models
    "JobResponse",
    "JobStatusResponse",
    "HealthResponse",
    "ErrorResponse",
    # Enums
    "JobStatus",
    "WorkflowMode",
    "EventType",
    # State models
    "StreamEvent",
    "JobState",
    "TaskInfo",
]
