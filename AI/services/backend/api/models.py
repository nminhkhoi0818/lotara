"""
API Models for Travel Lotara Backend

Pydantic v2 models for all HTTP requests and responses.
Strict typing for API contract with Next.js/TS backend.
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


class EventType(str, Enum):
    """SSE event types."""
    STATE_CHANGE = "state_change"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    AGENT_OUTPUT = "agent_output"
    VALIDATION_RESULT = "validation_result"
    ERROR = "error"
    COMPLETE = "complete"


# ============================================
# REQUEST MODELS
# ============================================

class PlanRequest(BaseModel):
    """
    Request to start reactive travel planning workflow.
    
    Example:
        {
            "user_id": "user123",
            "query": "Plan a 5-day trip to Tokyo for under $3000",
            "constraints": {
                "budget_usd": 3000,
                "duration_days": 5,
                "interests": ["food", "culture"],
                "departure_city": "LAX"
            }
        }
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "user123",
            "query": "Plan a 5-day trip to Tokyo for under $3000",
            "constraints": {
                "budget_usd": 3000,
                "duration_days": 5,
                "interests": ["food", "culture"],
                "departure_city": "LAX"
            }
        }
    })
    
    user_id: str = Field(..., description="Unique user identifier from product backend")
    query: str = Field(..., min_length=1, max_length=2000, description="Natural language travel request")
    constraints: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured constraints (budget, dates, preferences)"
    )
    session_id: Optional[str] = Field(None, description="Existing session to continue")


class SuggestRequest(BaseModel):
    """
    Request to trigger proactive suggestion workflow.
    
    Triggered by product backend when:
    - Price alert detected
    - Calendar gap identified  
    - Budget surplus found
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "user123",
            "trigger_type": "price_drop",
            "context": {
                "route": "LAX->NRT",
                "old_price": 850,
                "new_price": 650,
                "savings": 200
            }
        }
    })
    
    user_id: str = Field(..., description="User to receive suggestion")
    trigger_type: str = Field(..., description="What triggered this: price_drop, calendar_gap, budget_surplus")
    context: dict[str, Any] = Field(..., description="Trigger-specific context data")
    constraints: Optional[dict[str, Any]] = Field(None, description="User preferences")


class ApprovalRequest(BaseModel):
    """
    Human-in-the-loop approval for critical actions.
    
    Used for:
    - Booking confirmation
    - Budget override
    - Legal acknowledgment
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "approved": True,
            "notes": "Looks good, proceed with booking"
        }
    })
    
    job_id: str = Field(..., description="Job awaiting approval")
    approved: bool = Field(..., description="User's decision")
    notes: Optional[str] = Field(None, max_length=500, description="Optional user feedback")


class FeedbackRequest(BaseModel):
    """
    User feedback on completed workflow.
    
    Logged to Opik for evaluation and improvement.
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "rating": 5,
            "comment": "Perfect itinerary, exactly what I wanted!"
        }
    })
    
    job_id: str = Field(..., description="Completed job")
    rating: int = Field(..., ge=1, le=5, description="1-5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Free-text feedback")
    helpful_aspects: Optional[list[str]] = Field(None, description="What worked well")
    improvement_areas: Optional[list[str]] = Field(None, description="What could be better")


# ============================================
# RESPONSE MODELS
# ============================================

class JobResponse(BaseModel):
    """
    Response when job is created or completed.
    
    Frontend polls /status/{job_id} for updates.
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user123",
            "status": "started",
            "message": "Planning job started",
            "created_at": "2026-01-20T10:00:00Z"
        }
    })
    
    job_id: str = Field(..., description="Unique job identifier")
    user_id: str = Field(..., description="User who created the job")
    status: JobStatus = Field(..., description="Current job status")
    message: Optional[str] = Field(None, description="Human-readable status message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    result: Optional[dict[str, Any]] = Field(None, description="Job result (when completed)")


class TaskInfo(BaseModel):
    """Individual task within a workflow."""
    task_id: str
    agent: str
    task_name: str
    status: str  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[dict[str, Any]] = None
    confidence_score: Optional[float] = None


class JobStatusResponse(BaseModel):
    """
    Detailed job status.
    
    Returned by GET /status/{job_id}
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "executing",
            "mode": "reactive",
            "created_at": "2026-01-17T10:30:00Z",
            "updated_at": "2026-01-17T10:35:00Z",
            "progress": {
                "current_state": "execution",
                "tasks_total": 5,
                "tasks_completed": 3,
                "estimated_completion_seconds": 120
            },
            "current_output": {
                "flights": [...],
                "hotels": [...]
            }
        }
    })
    
    job_id: str
    status: JobStatus
    mode: WorkflowMode
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    progress: Optional[dict[str, Any]] = Field(
        None,
        description="Current progress: state, completed tasks, ETA"
    )
    
    # Partial results (streaming-compatible)
    current_output: Optional[dict[str, Any]] = Field(
        None,
        description="Partial results accumulated so far"
    )
    
    # Final results (when status=completed)
    final_result: Optional[dict[str, Any]] = Field(
        None,
        description="Complete itinerary (only when completed)"
    )
    
    # Error details (when status=failed)
    error: Optional[dict[str, Any]] = Field(
        None,
        description="Error details if job failed"
    )
    
    # Tasks
    tasks: Optional[list[TaskInfo]] = Field(
        None,
        description="Individual task status"
    )
    
    # Observability
    opik_trace_url: Optional[str] = Field(
        None,
        description="Link to Opik trace for debugging"
    )


class StreamEvent(BaseModel):
    """
    Server-Sent Event payload.
    
    Streamed via GET /stream/{job_id}
    """
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: dict[str, Any]
    
    def to_sse(self) -> str:
        """
        Convert to SSE format.
        
        Returns:
            event: {event_type}
            data: {json}
            
        """
        import json
        return (
            f"event: {self.event_type.value}\n"
            f"data: {json.dumps(self.data, default=str)}\n\n"
        )


# ============================================
# INTERNAL MODELS
# ============================================

class JobState(BaseModel):
    """
    Internal job state stored in Redis.
    
    Not exposed directly via API.
    """
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    mode: WorkflowMode
    status: JobStatus = JobStatus.STARTED
    
    # Request context
    query: Optional[str] = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    trigger_context: Optional[dict[str, Any]] = None
    
    # Execution state
    current_state: str = "monitoring"
    tasks: list[TaskInfo] = Field(default_factory=list)
    
    # Outputs
    partial_outputs: dict[str, Any] = Field(default_factory=dict)
    final_result: Optional[dict[str, Any]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Error tracking
    error: Optional[dict[str, Any]] = None
    
    # Observability
    opik_trace_id: Optional[str] = None
    opik_trace_url: Optional[str] = None
    
    # HITL
    awaiting_approval: bool = False
    approval_data: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    services: dict[str, str] = Field(
        default_factory=lambda: {
            "redis": "unknown",
            "opik": "unknown",
        }
    )


# ============================================
# ERROR MODELS
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    job_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[dict[str, Any]] = None
