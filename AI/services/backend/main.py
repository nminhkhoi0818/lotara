"""
Travel Lotara AI Backend

Production FastAPI backend for multi-agent travel concierge.

Architecture:
- API Layer: HTTP + SSE endpoints
- Workflow Layer: MotherAgent orchestration
- Job Layer: Redis-based async execution
- Observability: Full Opik integration

This backend is AI-only - no auth, billing, or frontend logic.
Product backend (Next.js/TS) handles authentication and calls these APIs.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError

from api.models import (
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
    StreamEvent,
)
from core.job_manager import JobManager
from core.workflow_executor import WorkflowExecutor
from src.travel_lotara.tracking.opik_tracker import get_opik_manager
from src.travel_lotara.database import get_supabase_client, JobRepository, FeedbackRepository


# ============================================
# LOGGING
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================
# LIFECYCLE MANAGEMENT
# ============================================

# Global instances
job_manager: Optional[JobManager] = None
workflow_executor: Optional[WorkflowExecutor] = None
opik_manager = get_opik_manager()
supabase_client = None
job_repository: Optional[JobRepository] = None
feedback_repository: Optional[FeedbackRepository] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown:
    - Connect to Redis
    - Initialize Supabase client
    - Initialize managers
    - Cleanup on shutdown
    """
    global job_manager, workflow_executor, supabase_client, job_repository, feedback_repository
    
    # Startup
    logger.info("Starting Travel Lotara AI Backend...")
    
    # Initialize Supabase client for database operations
    try:
        supabase_client = get_supabase_client()
        health = supabase_client.health_check()
        if health["connected"]:
            logger.info("✓ Supabase database connected")
            job_repository = JobRepository()
            feedback_repository = FeedbackRepository()
        else:
            logger.warning(f"⚠ Supabase connection issue: {health['message']}")
    except Exception as e:
        logger.warning(f"⚠ Supabase not configured: {e}. Running without database persistence.")
    
    # Initialize Redis-based job manager
    import os
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    job_manager = JobManager(redis_url=redis_url)
    await job_manager.connect()
    
    # Initialize workflow executor
    workflow_executor = WorkflowExecutor(job_manager)
    
    logger.info("✓ Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Travel Lotara AI Backend...")
    
    # Cancel active workflows
    if workflow_executor:
        await workflow_executor.cleanup()
    
    # Close Redis connection
    if job_manager:
        await job_manager.close()
    
    logger.info("✓ Backend shut down successfully")


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Travel Lotara AI Backend",
    description="Production AI backend for autonomous multi-agent travel concierge",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


# ============================================
# MIDDLEWARE
# ============================================

# CORS - Allow product backend to call these APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:5173",  # Vite dev
        "https://lotara.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Invalid request data",
            details={"errors": exc.errors()},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    
    Logs error to Opik and returns user-safe message.
    Never exposes stack traces to clients.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Log to Opik
    await opik_manager.log_error(
        error=exc,
        context={
            "path": request.url.path,
            "method": request.method,
        },
        tags=["backend_error", "unhandled"],
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred. Please try again.",
        ).model_dump(),
    )


# ============================================
# API ENDPOINTS
# ============================================

@app.post(
    "/v1/plan",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Workflows"],
    summary="Start reactive travel planning",
)
async def plan_trip(request: PlanRequest) -> JobResponse:
    """
    Start a user-requested travel planning workflow.
    
    **Reactive Mode**: User triggers via chat or form.
    
    **Process:**
    1. Create job
    2. Start async workflow
    3. Return job_id immediately
    4. Frontend polls /status or connects to /stream
    
    **Example Request:**
    ```json
    {
        "user_id": "user123",
        "query": "Plan a 5-day trip to Tokyo for under $3000",
        "constraints": {
            "budget_usd": 3000,
            "duration_days": 5,
            "interests": ["food", "culture"]
        }
    }
    ```
    
    **Example Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "started"
    }
    ```
    """
    # Create job
    job_id = await job_manager.create_job(
        user_id=request.user_id,
        mode=WorkflowMode.REACTIVE,
        query=request.query,
        constraints=request.constraints,
    )
    
    # Execute workflow in background
    await workflow_executor.execute_reactive_workflow(
        job_id=job_id,
        user_id=request.user_id,
        query=request.query,
        constraints=request.constraints,
    )
    
    return JobResponse(job_id=job_id, status=JobStatus.STARTED)


@app.post(
    "/v1/suggest",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Workflows"],
    summary="Start proactive suggestion workflow",
)
async def suggest_proactively(request: SuggestRequest) -> JobResponse:
    """
    Trigger proactive suggestion workflow.
    
    **Proactive Mode**: System triggers based on:
    - Price drop detected
    - Calendar gap identified
    - Budget surplus found
    
    **Called by:** Product backend (Next.js/TS) when opportunities detected.
    
    **Example Request:**
    ```json
    {
        "user_id": "user123",
        "trigger_type": "price_drop",
        "context": {
            "route": "LAX->NRT",
            "old_price": 850,
            "new_price": 650,
            "savings": 200
        }
    }
    ```
    """
    # Create job
    job_id = await job_manager.create_job(
        user_id=request.user_id,
        mode=WorkflowMode.PROACTIVE,
        trigger_context=request.context,
        constraints=request.constraints,
    )
    
    # Execute workflow in background
    await workflow_executor.execute_proactive_workflow(
        job_id=job_id,
        user_id=request.user_id,
        trigger_type=request.trigger_type,
        trigger_context=request.context,
        constraints=request.constraints,
    )
    
    return JobResponse(job_id=job_id, status=JobStatus.STARTED)


@app.get(
    "/v1/status/{job_id}",
    response_model=JobStatusResponse,
    tags=["Jobs"],
    summary="Get job status",
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get current status and progress of a job.
    
    **Polling**: Frontend polls this endpoint every 2-5 seconds.
    
    **Better Alternative**: Use /stream for real-time updates.
    
    **Response includes:**
    - Current status (started, planning, executing, completed, failed)
    - Workflow state (monitoring, intake, planning, execution)
    - Progress (tasks completed, ETA)
    - Partial outputs (flights, hotels discovered so far)
    - Final result (when completed)
    - Error details (if failed)
    - Opik trace URL (for debugging)
    """
    state = await job_manager.get_job(job_id)
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )
    
    # Calculate progress
    total_tasks = len(state.tasks)
    completed_tasks = sum(1 for t in state.tasks if t.status == "completed")
    
    return JobStatusResponse(
        job_id=state.job_id,
        status=state.status,
        mode=state.mode,
        created_at=state.created_at,
        updated_at=state.updated_at,
        completed_at=state.completed_at,
        progress={
            "current_state": state.current_state,
            "tasks_total": total_tasks,
            "tasks_completed": completed_tasks,
        } if total_tasks > 0 else None,
        current_output=state.partial_outputs if state.partial_outputs else None,
        final_result=state.final_result,
        error=state.error,
        tasks=state.tasks,
        opik_trace_url=state.opik_trace_url,
    )


@app.get(
    "/v1/stream/{job_id}",
    tags=["Jobs"],
    summary="Stream job events (SSE)",
)
async def stream_job_events(job_id: str):
    """
    Stream job events in real-time using Server-Sent Events (SSE).
    
    **Best for UX**: Updates frontend immediately as workflow progresses.
    
    **Event Types:**
    - `state_change`: Workflow state updated
    - `task_start`: Agent started working
    - `task_complete`: Agent finished
    - `agent_output`: Partial results available
    - `validation_result`: Validation passed/failed
    - `error`: Something went wrong
    - `complete`: Job finished
    
    **Usage:**
    ```javascript
    const eventSource = new EventSource('/v1/stream/job-id');
    
    eventSource.addEventListener('agent_output', (e) => {
        const data = JSON.parse(e.data);
        console.log('New results:', data);
    });
    
    eventSource.addEventListener('complete', (e) => {
        eventSource.close();
    });
    ```
    """
    # Verify job exists
    state = await job_manager.get_job(job_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )
    
    async def event_generator():
        """Generate SSE events."""
        try:
            async for event in job_manager.stream_events(job_id):
                yield event.to_sse()
        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for job {job_id}")
        except Exception as e:
            logger.error(f"SSE stream error: {e}", exc_info=True)
            # Send error event
            error_event = StreamEvent(
                event_type="error",
                data={"message": "Stream error occurred"}
            )
            yield error_event.to_sse()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.post(
    "/v1/approve",
    status_code=status.HTTP_200_OK,
    tags=["HITL"],
    summary="Approve pending action",
)
async def approve_action(request: ApprovalRequest):
    """
    Human-in-the-loop approval for critical actions.
    
    **When Required:**
    - Booking confirmation (charge money)
    - Budget override (exceed limit)
    - Legal acknowledgment (visa requirements)
    
    **Process:**
    1. Workflow pauses with status=`waiting_approval`
    2. Frontend shows approval modal
    3. User approves/rejects
    4. This endpoint called
    5. Workflow resumes or cancels
    
    **Example:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "approved": true,
        "notes": "Looks good, proceed with booking"
    }
    ```
    """
    state = await job_manager.get_job(request.job_id)
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {request.job_id} not found",
        )
    
    if not state.awaiting_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not awaiting approval",
        )
    
    # Update approval state
    state.awaiting_approval = False
    state.approval_data["approved"] = request.approved
    state.approval_data["notes"] = request.notes
    
    if request.approved:
        # Resume workflow
        state.status = JobStatus.EXECUTING
        await job_manager._save_job(state)
        
        # Note: Workflow will check approval state and continue
        # This is handled in WorkflowExecutor
        
        return {"message": "Approval granted, workflow resuming"}
    else:
        # Cancel workflow
        await workflow_executor.cancel_workflow(request.job_id)
        
        return {"message": "Approval denied, workflow cancelled"}


@app.post(
    "/v1/feedback",
    status_code=status.HTTP_200_OK,
    tags=["Evaluation"],
    summary="Submit user feedback",
)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit user feedback on completed workflow.
    
    **Purpose:**
    - Improve AI over time
    - Evaluate agent performance
    - Identify failure patterns
    
    **Logged to Opik** for:
    - LLM-as-judge evaluation
    - A/B testing
    - Performance dashboards
    
    **Example:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "rating": 5,
        "comment": "Perfect itinerary!",
        "helpful_aspects": ["budget_accuracy", "creative_suggestions"],
        "improvement_areas": ["flight_times"]
    }
    ```
    """
    state = await job_manager.get_job(request.job_id)
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {request.job_id} not found",
        )
    
    # Log feedback to Opik
    if state.opik_trace_id:
        await opik_manager.log_feedback(
            trace_id=state.opik_trace_id,
            score=request.rating / 5.0,  # Normalize to 0-1
            metadata={
                "comment": request.comment,
                "helpful_aspects": request.helpful_aspects,
                "improvement_areas": request.improvement_areas,
                "user_id": state.user_id,
                "job_id": request.job_id,
            },
            tags=["user_feedback"],
        )
    
    return {"message": "Feedback submitted successfully"}


# ============================================
# HEALTH & MONITORING
# ============================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    **Used by:**
    - Load balancers
    - Kubernetes readiness probes
    - Monitoring systems
    
    **Checks:**
    - Redis connection
    - Supabase database connection
    - Opik connection
    """
    services = {
        "redis": "unknown",
        "supabase": "unknown",
        "opik": "unknown",
    }
    
    # Check Redis
    try:
        await job_manager.redis.ping()
        services["redis"] = "healthy"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)}"
    
    # Check Supabase
    try:
        if supabase_client:
            health = supabase_client.health_check()
            services["supabase"] = "healthy" if health["connected"] else f"unhealthy: {health['message']}"
        else:
            services["supabase"] = "not_configured"
    except Exception as e:
        services["supabase"] = f"unhealthy: {str(e)}"
    
    # Check Opik
    try:
        # Simple check - Opik manager initialized
        if opik_manager:
            services["opik"] = "healthy"
    except Exception as e:
        services["opik"] = f"unhealthy: {str(e)}"
    
    overall_status = "healthy" if all(
        s in ("healthy", "not_configured") for s in services.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        services=services,
    )


@app.get(
    "/",
    tags=["System"],
    summary="Root endpoint",
)
async def root():
    """API root - redirect to docs."""
    return {
        "message": "Travel Lotara AI Backend",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
    }


# ============================================
# DEVELOPMENT HELPERS
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
