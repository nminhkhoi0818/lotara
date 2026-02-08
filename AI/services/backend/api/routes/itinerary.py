"""Itinerary generation endpoint with SSE streaming."""

import sys
import os
import json
import hashlib
import asyncio
import time
from functools import lru_cache
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from services.backend.api.models import ItineraryRequest, ItineraryResponse
from sse_starlette.sse import EventSourceResponse

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

# Import validation utilities
from services.backend.api.validators.itinerary_validator import (
    validate_itinerary_structure,
    normalize_itinerary_output
)

router = APIRouter(prefix="/api/itinerary", tags=["itinerary"])

# Simple in-memory cache (works in single-worker mode)
# WARNING: This cache is NOT shared across multiple workers/processes
# For multi-worker deployments, use Redis or similar distributed cache

# Cache storage (persists during worker lifetime)
_cache_storage = {}
_cache_lock = asyncio.Lock()  # Prevent race conditions

def generate_cache_key(request_dict: dict) -> str:
    """Generate cache key from request parameters"""
    cache_string = json.dumps(request_dict, sort_keys=True)
    return hashlib.md5(cache_string.encode()).hexdigest()

async def get_from_cache(cache_key: str):
    """Get from in-memory cache (async-safe)"""
    async with _cache_lock:
        return _cache_storage.get(cache_key)

async def save_to_cache(cache_key: str, result: dict):
    """Save to in-memory cache (async-safe)"""
    async with _cache_lock:
        # Limit cache size to prevent memory issues
        if len(_cache_storage) >= 100:
            # Remove oldest entry (FIFO)
            oldest_key = next(iter(_cache_storage))
            del _cache_storage[oldest_key]
        _cache_storage[cache_key] = result


@router.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    """
    Generate a personalized travel itinerary using AI agents.
    
    ⚠️ Note: This endpoint may take 30-120 seconds. 
    Use /generate-stream for real-time progress updates (recommended).
    """
    
    # Lazy import to reduce cold start time
    from src.travel_lotara.main import run_agent
    from src.travel_lotara.tracking import flush_traces
    from services.backend.api.app import request_semaphore
    
    # Check cache first
    request_dict = request.model_dump()
    cache_key = generate_cache_key(request_dict)
    
    cached_result = await get_from_cache(cache_key)
    if cached_result:
        print(f"[CACHE HIT] Returning cached result")
        return ItineraryResponse(**cached_result)
    
    # Use semaphore to limit concurrent requests
    async with request_semaphore:
        print(f"[REQUEST] Acquired semaphore, processing request...")
        
        # Retry configuration
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                print(f"[ATTEMPT {attempt + 1}/{max_retries}] Generating itinerary...")
                
                # Run the agent system
                response_text, session = await run_agent(
                    user_input="",
                    user_id=request.userId,
                    backend_json=request_dict,
                )
                
                print(f"[DEBUG] Raw agent response type: {type(response_text)}")
                print(f"[DEBUG] Raw agent response preview: {str(response_text)[:200]}...")
                
                # Normalize the output structure
                normalized_data = normalize_itinerary_output(response_text)
                print(f"[DEBUG] Normalized data keys: {list(normalized_data.keys())}")
                
                # Validate the structure
                validation_result = validate_itinerary_structure(normalized_data)
                
                if validation_result.warnings:
                    print(f"[WARNINGS] {len(validation_result.warnings)} warnings:")
                    for warning in validation_result.warnings:
                        print(f"  - {warning}")
                
                if validation_result.is_valid:
                    print(f"[SUCCESS] Itinerary validation passed")
                    
                    # Extract metadata from itinerary for top-level fields
                    itinerary_obj = validation_result.itinerary
                    
                    # Note: Evaluation already done in main.py run_agent() - no need to duplicate
                    
                    result = {
                        "status": "completed",
                        "session_id": session.id if session else "unknown",
                        "user_id": request.userId,
                        "itinerary": itinerary_obj,
                        "error": "null",
                    }
                    
                    # Cache the successful result
                    await save_to_cache(cache_key, result)
                    
                    return ItineraryResponse(**result)
                else:
                    # Validation failed
                    error_msg = f"Validation failed: {'; '.join(validation_result.errors)}"
                    print(f"[ERROR] {error_msg}")
                    
                    if attempt < max_retries - 1:
                        print(f"[RETRY] Attempt {attempt + 1} failed validation, retrying...")
                        last_error = error_msg
                        # Wait a bit before retry
                        await asyncio.sleep(2)
                        continue
                    else:
                        # Last attempt failed, return with errors
                        print(f"[FINAL ERROR] All {max_retries} attempts failed validation")
                        result = {
                            "status": "failed",
                            "session_id": session.id if session else "unknown",
                            "user_id": request.userId,
                            "itinerary": normalized_data,  # Return normalized data anyway
                            "error": f"Validation failed after {max_retries} attempts. Errors: {'; '.join(validation_result.errors)}"
                        }
                        return ItineraryResponse(**result)
            
            except Exception as e:
                error_msg = str(e)
                print(f"[ERROR] Attempt {attempt + 1} failed with exception: {error_msg[:200]}")
                last_error = error_msg
                
                # Check if it's a retryable error
                if "503" in error_msg or "overloaded" in error_msg.lower():
                    if attempt < max_retries - 1:
                        print(f"[RETRY] Service overloaded, waiting before retry...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        raise HTTPException(
                            status_code=503,
                            detail={
                                "error": "ServiceUnavailable",
                                "message": "AI service is temporarily overloaded. Please try again in a few minutes.",
                                "details": error_msg[:200]
                            }
                        )
                elif "429" in error_msg or "rate limit" in error_msg.lower():
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "RateLimitExceeded",
                            "message": "Google Gemini API rate limit exceeded. Please wait 5-10 minutes.",
                            "details": error_msg[:200]
                        }
                    )
                else:
                    if attempt < max_retries - 1:
                        print(f"[RETRY] Unexpected error, retrying...")
                        await asyncio.sleep(2)
                        continue
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail={
                                "error": "InternalServerError",
                                "message": "Failed to generate itinerary",
                                "details": error_msg[:200]
                            }
                        )
    
    # Flush traces regardless of success/failure
    flush_traces()
    
    # Should not reach here, but just in case
    raise HTTPException(
        status_code=500,
        detail={
            "error": "InternalServerError",
            "message": f"Failed after {max_retries} attempts",
            "details": str(last_error)[:200] if last_error else "Unknown error"
        }
    )


@router.post("/generate-stream")
async def generate_itinerary_stream(request: ItineraryRequest):
    """
    Generate itinerary with REAL-TIME Server-Sent Events (SSE) streaming.
    
    Returns live progress updates as agents execute, showing actual thinking process:
    - Tool calls (Milvus searches, location lookups)
    - Agent transitions (Inspiration → Planning → Detailing)
    - Model responses and thinking
    - Validation steps
    
    Client receives events:
    - event: progress, data: {"type": "agent_started", "message": "Inspiration Agent starting...", "progress": 20}
    - event: progress, data: {"type": "tool_call", "message": "🔍 Searching database for Bangkok...", "progress": 25}  
    - event: progress, data: {"type": "model_call", "message": "💭 Generating trip themes...", "progress": 35}
    - event: done, data: {full itinerary result}
    - event: error, data: {error details}
    
    Uses ProgressTracker to capture actual agent callback events in real-time.
    """
    
    # Lazy imports
    from src.travel_lotara.main import run_agent
    from src.travel_lotara.tracking import flush_traces, ProgressTracker
    
    # Check cache
    request_dict = request.model_dump()
    cache_key = generate_cache_key(request_dict)
    
    cached_result = await get_from_cache(cache_key)
    if cached_result:
        async def send_cached():
            yield {
                "event": "cache_hit",
                "data": json.dumps({"message": "Retrieved from cache (instant!)", "progress": 100})
            }
            yield {
                "event": "done",
                "data": json.dumps(cached_result)
            }
        
        return EventSourceResponse(send_cached())
    
    async def event_generator():
        # Use semaphore to limit concurrent requests
        from services.backend.api.app import request_semaphore
        
        async with request_semaphore:
            print(f"[STREAM] Acquired semaphore, processing request...")
            
            # Create a unique session ID for this request
            session_id = f"stream_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
            tracker = None
            
            try:
                # Send initial progress
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "type": "started",
                        "message": "Initializing AI agents...",
                        "progress": 0,
                        "status": "started"
                    })
                }
                
                # Retry configuration
                max_retries = 2
                
                for attempt in range(max_retries):
                    try:
                        if attempt > 0:
                            yield {
                                "event": "retry",
                                "data": json.dumps({
                                    "type": "retry",
                                    "message": f"Retrying attempt {attempt + 1}/{max_retries}...",
                                    "progress": 0,
                                    "status": "retrying"
                                })
                            }
                            await asyncio.sleep(2)
                        
                        # Create progress tracker for this session
                        tracker = await ProgressTracker.get_tracker(session_id)
                        
                        # Start agent execution task
                        agent_task = asyncio.create_task(run_agent(
                            user_input="",
                            user_id=request.userId,
                            backend_json=request_dict,
                        ))
                        
                        # Stream real-time progress events from tracker
                        progress_task = asyncio.create_task(
                            stream_progress_events(tracker, session_id)
                        )
                        
                        async for event in progress_task:
                            yield event
                            
                            # Check if agent task completed
                            if agent_task.done():
                                break
                        
                        # Get result
                        response_text, session = await agent_task
                        
                        # Mark tracker as validating
                        tracker.add_event(
                            "validation",
                            "Validating itinerary structure...",
                            progress=95
                        )
                        
                        yield {
                            "event": "progress",
                            "data": json.dumps({
                                "type": "validation",
                                "message": "Validating itinerary...",
                                "progress": 95,
                                "status": "validating"
                            })
                        }
                        
                        # Extract and validate itinerary
                        itinerary_data = None
                        if session and hasattr(session, 'state'):
                            state_itinerary = session.state.get("itinerary")
                            if state_itinerary and isinstance(state_itinerary, dict):
                                itinerary_data = state_itinerary
                        
                        if not itinerary_data:
                            try:
                                itinerary_data = json.loads(response_text)
                            except json.JSONDecodeError:
                                itinerary_data = {
                                    "raw_response": response_text,
                                    "note": "Response was not in expected JSON format"
                                }
                        
                        # Normalize the output structure
                        normalized_data = normalize_itinerary_output(itinerary_data)
                        
                        # Validate the structure
                        validation_result = validate_itinerary_structure(normalized_data)
                        
                        if validation_result.is_valid:
                            # Success!
                            tracker.mark_complete("Itinerary generated successfully!")
                            
                            itinerary_obj = validation_result.itinerary
                            
                            # Note: Evaluation already done in main.py run_agent() - no need to duplicate
                            
                            result = {
                                "status": "completed",
                                "session_id": session.id if session else session_id,
                                "user_id": request.userId,
                                "itinerary": itinerary_obj,
                                "error": None
                            }
                            
                            # Cache the result
                            await save_to_cache(cache_key, result)
                            
                            # Send completion
                            yield {
                                "event": "done",
                                "data": json.dumps(result)
                            }
                            
                            return  # Success - exit the retry loop
                        else:
                            # Validation failed
                            if attempt < max_retries - 1:
                                tracker.add_event(
                                    "warning",
                                    f"Validation failed, retrying... ({attempt + 1}/{max_retries})",
                                    progress=10
                                )
                                
                                yield {
                                    "event": "validation_failed",
                                    "data": json.dumps({
                                        "type": "warning",
                                        "message": f"Validation failed, retrying... (attempt {attempt + 1}/{max_retries})",
                                        "errors": validation_result.errors[:3],
                                        "status": "retrying"
                                    })
                                }
                                continue  # Retry
                            else:
                                # Last attempt failed
                                tracker.mark_error(f"Validation failed: {'; '.join(validation_result.errors[:2])}")
                                
                                result = {
                                    "status": "failed",
                                    "session_id": session.id if session else session_id,
                                    "user_id": request.userId,
                                    "itinerary": normalized_data,
                                    "error": f"Validation failed after {max_retries} attempts. Errors: {'; '.join(validation_result.errors)}"
                                }
                                
                                yield {
                                    "event": "error",
                                    "data": json.dumps({
                                        "type": "error",
                                        "error": "Validation failed",
                                        "message": result["error"],
                                        "details": validation_result.errors
                                    })
                                }
                                return
                    
                    except Exception as e:
                        error_msg = str(e)
                        
                        if tracker:
                            tracker.mark_error(error_msg[:100])
                        
                        if attempt < max_retries - 1:
                            yield {
                                "event": "error_retry",
                                "data": json.dumps({
                                    "type": "error",
                                    "message": f"Error occurred, retrying... (attempt {attempt + 1}/{max_retries})",
                                    "error": error_msg[:100],
                                    "status": "retrying"
                                })
                            }
                            await asyncio.sleep(3)
                            continue  # Retry
                        else:
                            # Last attempt failed with exception
                            yield {
                                "event": "error",
                                "data": json.dumps({
                                    "type": "error",
                                    "error": "Failed to generate itinerary",
                                    "details": error_msg[:200]
                                })
                            }
                            return
            
            finally:
                # Cleanup tracker
                if tracker:
                    await ProgressTracker.remove_tracker(session_id)
                flush_traces()
    
    return EventSourceResponse(event_generator())


async def stream_progress_events(tracker: "ProgressTracker", session_id: str):
    """
    Stream progress events from tracker to SSE client.
    
    This async generator yields SSE-formatted events from the ProgressTracker
    as agents execute and callbacks fire.
    """
    import time
    
    async for event in tracker.stream_events(timeout=180.0):
        yield {
            "event": "progress",
            "data": json.dumps(event.to_dict())
        }
        
        # Small delay to prevent overwhelming the client
        await asyncio.sleep(0.1)


@router.get("/cache-status")
async def get_cache_status():
    """Get cache statistics"""
    return {
        "cache_size": len(_cache_storage),
        "cache_limit": 100,
        "message": f"{len(_cache_storage)} itineraries cached in memory"
    }

