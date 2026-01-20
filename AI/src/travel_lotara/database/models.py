"""
Database Models for Travel Lotara.

Pydantic models representing database table structures.
These map directly to Supabase/PostgreSQL tables.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


# ============================================
# ENUMS
# ============================================

class JobStatus(str, Enum):
    """Job execution status."""
    STARTED = "started"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowMode(str, Enum):
    """Workflow execution mode."""
    REACTIVE = "reactive"  # User-triggered
    PROACTIVE = "proactive"  # System-triggered


# ============================================
# DATABASE MODELS
# ============================================

class JobRecord(BaseModel):
    """
    Job record stored in the database.
    
    Maps to: public.jobs table
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    session_id: Optional[str] = None
    
    # Job configuration
    mode: WorkflowMode = WorkflowMode.REACTIVE
    status: JobStatus = JobStatus.STARTED
    query: Optional[str] = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    trigger_context: Optional[dict[str, Any]] = None
    
    # Execution state
    current_state: str = "monitoring"
    tasks: list[dict[str, Any]] = Field(default_factory=list)
    
    # Outputs
    partial_outputs: dict[str, Any] = Field(default_factory=dict)
    final_result: Optional[dict[str, Any]] = None
    
    # Error tracking
    error: Optional[dict[str, Any]] = None
    
    # Observability
    opik_trace_id: Optional[str] = None
    opik_trace_url: Optional[str] = None
    
    # Human-in-the-loop
    awaiting_approval: bool = False
    approval_data: Optional[dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class SessionRecord(BaseModel):
    """
    User session record for conversation context.
    
    Maps to: public.sessions table
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    
    # Session state
    is_active: bool = True
    context: dict[str, Any] = Field(default_factory=dict)
    
    # Conversation history (limited for free tier)
    messages: list[dict[str, Any]] = Field(default_factory=list)
    
    # User preferences captured during session
    captured_preferences: dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackRecord(BaseModel):
    """
    User feedback on completed workflows.
    
    Maps to: public.feedback table
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    user_id: str
    
    # Feedback content
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    helpful_aspects: list[str] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserPreferenceRecord(BaseModel):
    """
    Persistent user preferences.
    
    Maps to: public.user_preferences table
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    
    # Travel preferences
    preferred_destinations: list[str] = Field(default_factory=list)
    budget_range: Optional[dict[str, float]] = None  # {min: 0, max: 5000}
    travel_style: Optional[str] = None  # luxury, budget, adventure, etc.
    dietary_restrictions: list[str] = Field(default_factory=list)
    accessibility_needs: list[str] = Field(default_factory=list)
    
    # Communication preferences
    preferred_language: str = "en"
    notification_settings: dict[str, bool] = Field(
        default_factory=lambda: {
            "price_alerts": True,
            "trip_reminders": True,
            "proactive_suggestions": True,
        }
    )
    
    # Historical data
    past_destinations: list[str] = Field(default_factory=list)
    favorite_activities: list[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TravelItineraryRecord(BaseModel):
    """
    Saved travel itinerary.
    
    Maps to: public.itineraries table
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    user_id: str
    
    # Itinerary details
    title: str
    destination: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Full itinerary data
    itinerary_data: dict[str, Any] = Field(default_factory=dict)
    
    # Status
    is_booked: bool = False
    booking_references: list[dict[str, Any]] = Field(default_factory=list)
    
    # Estimated costs
    estimated_total_cost: Optional[float] = None
    currency: str = "USD"
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
