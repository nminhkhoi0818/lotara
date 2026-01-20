"""
Travel Lotara AI Backend - Vercel Serverless Entry Point

FastAPI app for Vercel serverless deployment.
Uses Supabase for stateless database operations.

Vercel natively supports ASGI apps - just export `app` variable.
No Mangum adapter needed!

Deployment:
    1. Set environment variables in Vercel dashboard
    2. Deploy: vercel --prod
"""

import os
import logging
from datetime import datetime
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Import models from the same directory
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
)

# ============================================
# LOGGING
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================
# SUPABASE CLIENT (LAZY LOADED)
# ============================================

_supabase_client = None


def get_supabase():
    """Lazy-load Supabase client for serverless."""
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
            if url and key:
                _supabase_client = create_client(url, key)
                logger.info("Supabase client initialized")
        except Exception as e:
            logger.warning(f"Supabase not available: {e}")
    return _supabase_client


# ============================================
# LIFESPAN EVENTS
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan for startup/shutdown."""
    # Startup
    logger.info("Starting Travel Lotara AI Backend...")
    yield
    # Shutdown (limited to 500ms on Vercel)
    logger.info("Shutting down...")


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Travel Lotara AI Backend",
    description="Serverless AI backend for autonomous multi-agent travel concierge",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================
# MIDDLEWARE
# ============================================

# Get allowed origins from environment
cors_origins = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins + ["https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Invalid request data",
            details={"errors": exc.errors()},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
        ).model_dump(),
    )


# ============================================
# HEALTH & INFO ENDPOINTS
# ============================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Travel Lotara AI Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint with database status."""
    db_status = "disconnected"
    db_latency = None
    
    client = get_supabase()
    if client:
        try:
            start = datetime.utcnow()
            # Simple query to test connection
            client.table("health_check").select("id").limit(1).execute()
            db_latency = (datetime.utcnow() - start).total_seconds() * 1000
            db_status = "connected"
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            db_status = f"error: {str(e)[:50]}"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database=db_status,
        database_latency_ms=db_latency,
    )


# ============================================
# PLANNING ENDPOINTS
# ============================================

@app.post("/v1/plan", response_model=JobResponse, tags=["Planning"])
async def plan_trip(request: PlanRequest, background_tasks: BackgroundTasks):
    """
    Start a reactive travel planning workflow.
    
    Creates a new job and begins processing the travel request.
    Returns immediately with job_id for status tracking.
    
    The actual planning happens asynchronously.
    """
    import uuid
    from .orchestrator import get_travel_orchestrator
    
    job_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    
    # Store job in Supabase
    client = get_supabase()
    if client:
        try:
            client.table("jobs").insert({
                "id": job_id,
                "user_id": request.user_id,
                "mode": "reactive",
                "status": JobStatus.STARTED.value,
                "query": request.query,
                "constraints": request.constraints,
                "created_at": timestamp.isoformat(),
                "updated_at": timestamp.isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create job"
            )
    
    # Process the request (in serverless, this runs synchronously but quickly)
    orchestrator = get_travel_orchestrator(client)
    
    try:
        result = await orchestrator.process_plan_request(
            job_id=job_id,
            user_id=request.user_id,
            query=request.query,
            constraints=request.constraints,
        )
        return JobResponse(
            job_id=job_id,
            user_id=request.user_id,
            status=JobStatus.COMPLETED if result.get("status") == "completed" else JobStatus.WAITING_APPROVAL,
            message=result.get("message", "Planning complete"),
            created_at=timestamp,
            result=result.get("result"),
        )
    except Exception as e:
        logger.error(f"Planning failed: {e}")
        return JobResponse(
            job_id=job_id,
            user_id=request.user_id,
            status=JobStatus.FAILED,
            message=f"Planning failed: {str(e)}",
            created_at=timestamp,
        )


@app.post("/v1/suggest", response_model=JobResponse, tags=["Planning"])
async def suggest_trip(request: SuggestRequest):
    """
    Trigger proactive suggestion workflow.
    
    Called by product backend when opportunities are detected.
    """
    import uuid
    from .orchestrator import get_suggestion_orchestrator
    
    job_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    
    client = get_supabase()
    if client:
        try:
            client.table("jobs").insert({
                "id": job_id,
                "user_id": request.user_id,
                "mode": "proactive",
                "status": JobStatus.STARTED.value,
                "trigger_context": {
                    "trigger_type": request.trigger_type,
                    "trigger_data": request.trigger_data,
                },
                "created_at": timestamp.isoformat(),
                "updated_at": timestamp.isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to create suggestion job: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create suggestion job"
            )
    
    # Process the suggestion
    orchestrator = get_suggestion_orchestrator(client)
    
    try:
        result = await orchestrator.process_suggestion(
            job_id=job_id,
            user_id=request.user_id,
            trigger_type=request.trigger_type,
            trigger_data=request.trigger_data or {},
        )
        return JobResponse(
            job_id=job_id,
            user_id=request.user_id,
            status=JobStatus.COMPLETED,
            message="Suggestion generated",
            created_at=timestamp,
            result=result,
        )
    except Exception as e:
        logger.error(f"Suggestion failed: {e}")
        return JobResponse(
            job_id=job_id,
            user_id=request.user_id,
            status=JobStatus.FAILED,
            message=f"Suggestion failed: {str(e)}",
            created_at=timestamp,
        )


# ============================================
# JOB STATUS ENDPOINTS
# ============================================

@app.get("/v1/status/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
async def get_job_status(job_id: str):
    """Get the current status of a job."""
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        result = client.table("jobs").select("*").eq("id", job_id).single().execute()
        job = result.data
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        return JobStatusResponse(
            job_id=job["id"],
            status=JobStatus(job["status"]),
            progress=job.get("progress", 0),
            current_step=job.get("current_step"),
            result=job.get("result"),
            error=job.get("error"),
            created_at=datetime.fromisoformat(job["created_at"]),
            updated_at=datetime.fromisoformat(job["updated_at"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job status"
        )


@app.get("/v1/jobs/{user_id}", tags=["Jobs"])
async def list_user_jobs(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    status_filter: Optional[str] = None,
):
    """List all jobs for a user with optional filtering."""
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        query = client.table("jobs").select("*").eq("user_id", user_id)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return {
            "jobs": result.data,
            "count": len(result.data),
            "offset": offset,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list jobs"
        )


# ============================================
# APPROVAL & FEEDBACK ENDPOINTS
# ============================================

@app.post("/v1/approve", tags=["Approval"])
async def approve_recommendation(request: ApprovalRequest):
    """Approve or reject a recommendation."""
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        # Update job with approval
        client.table("jobs").update({
            "status": JobStatus.COMPLETED.value if request.approved else JobStatus.CANCELLED.value,
            "approval_response": {
                "approved": request.approved,
                "modifications": request.modifications,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", request.job_id).execute()
        
        return {
            "success": True,
            "job_id": request.job_id,
            "approved": request.approved,
            "message": "Recommendation approved" if request.approved else "Recommendation rejected",
        }
    except Exception as e:
        logger.error(f"Failed to process approval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process approval"
        )


@app.post("/v1/feedback", tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a completed job."""
    import uuid
    
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        feedback_id = str(uuid.uuid4())
        
        client.table("feedback").insert({
            "id": feedback_id,
            "job_id": request.job_id,
            "user_id": request.user_id,
            "rating": request.rating,
            "comment": request.comment,
            "categories": request.categories,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback submitted successfully",
        }
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


# ============================================
# USER PREFERENCES ENDPOINTS
# ============================================

@app.get("/v1/preferences/{user_id}", tags=["Preferences"])
async def get_user_preferences(user_id: str):
    """Get user preferences."""
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        result = client.table("user_preferences").select("*").eq("user_id", user_id).single().execute()
        
        if not result.data:
            # Return default preferences
            return {
                "user_id": user_id,
                "preferences": {},
                "created_at": None,
            }
        
        return result.data
    except Exception as e:
        logger.error(f"Failed to get preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve preferences"
        )


@app.put("/v1/preferences/{user_id}", tags=["Preferences"])
async def update_user_preferences(user_id: str, preferences: dict[str, Any]):
    """Update user preferences."""
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        # Upsert preferences
        client.table("user_preferences").upsert({
            "user_id": user_id,
            "preferences": preferences,
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "Preferences updated",
        }
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


# ============================================
# SYNCHRONOUS PLANNING (FOR DEMO)
# ============================================

@app.post("/v1/plan/sync", tags=["Planning"])
async def plan_trip_sync(request: PlanRequest):
    """
    Synchronous travel planning - returns complete result.
    
    Use this for demos and testing. For production, use /v1/plan
    and poll /v1/status/{job_id} for progress.
    """
    import uuid
    from .orchestrator import get_travel_orchestrator
    
    job_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    
    client = get_supabase()
    
    # Store job
    if client:
        try:
            client.table("jobs").insert({
                "id": job_id,
                "user_id": request.user_id,
                "mode": "reactive",
                "status": JobStatus.STARTED.value,
                "query": request.query,
                "constraints": request.constraints,
                "created_at": timestamp.isoformat(),
                "updated_at": timestamp.isoformat(),
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store job: {e}")
    
    # Process synchronously
    orchestrator = get_travel_orchestrator(client)
    
    try:
        result = await orchestrator.process_plan_request(
            job_id=job_id,
            user_id=request.user_id,
            query=request.query,
            constraints=request.constraints,
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "user_id": request.user_id,
            "query": request.query,
            "result": result.get("result"),
            "requires_approval": result.get("requires_approval", False),
            "message": result.get("message", "Planning complete"),
            "created_at": timestamp.isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Planning failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Planning failed: {str(e)}"
        )


# ============================================
# ITINERARY ENDPOINTS
# ============================================

@app.get("/v1/itineraries/{user_id}", tags=["Itineraries"])
async def list_user_itineraries(
    user_id: str,
    limit: int = 10,
    status_filter: Optional[str] = None,
):
    """List all itineraries for a user."""
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        query = client.table("itineraries").select("*").eq("user_id", user_id)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        
        return {
            "itineraries": result.data,
            "count": len(result.data),
        }
    except Exception as e:
        logger.error(f"Failed to list itineraries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list itineraries"
        )


@app.get("/v1/itinerary/{itinerary_id}", tags=["Itineraries"])
async def get_itinerary(itinerary_id: str):
    """Get a specific itinerary by ID."""
    client = get_supabase()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        result = client.table("itineraries").select("*").eq("id", itinerary_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Itinerary {itinerary_id} not found"
            )
        
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get itinerary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve itinerary"
        )
