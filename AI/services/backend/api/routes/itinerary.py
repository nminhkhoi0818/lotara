"""Itinerary generation endpoint with SSE streaming."""

import sys
import os
import json
import hashlib
import asyncio
from functools import lru_cache
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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

# Simple in-memory cache (limited but sufficient for Vercel)
# LRU cache holds last 100 requests in memory
@lru_cache(maxsize=100)
def get_cached_itinerary(cache_key: str):
    """Check if itinerary is in memory cache"""
    return None  # Will be populated by set_cached_itinerary


# Cache storage (persists during function lifetime)
_cache_storage = {}

def generate_cache_key(request_dict: dict) -> str:
    """Generate cache key from request parameters"""
    cache_string = json.dumps(request_dict, sort_keys=True)
    return hashlib.md5(cache_string.encode()).hexdigest()

def get_from_cache(cache_key: str):
    """Get from in-memory cache"""
    return _cache_storage.get(cache_key)

def save_to_cache(cache_key: str, result: dict):
    """Save to in-memory cache"""
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
    
    # Check cache first
    request_dict = request.model_dump()
    cache_key = generate_cache_key(request_dict)
    
    cached_result = get_from_cache(cache_key)
    if cached_result:
        print(f"[CACHE HIT] Returning cached result")
        return ItineraryResponse(**cached_result)
    
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
                
                result = {
                    "status": "completed",
                    "session_id": session.id if session else "unknown",
                    "user_id": request.userId,
                    "itinerary": itinerary_obj,
                    "error": "null",
                }
                
                # Cache the successful result
                save_to_cache(cache_key, result)
                
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
    Generate itinerary with Server-Sent Events (SSE) streaming.
    
    Returns real-time progress updates as agents execute.
    Best for user experience - shows progress instead of blank wait.
    
    Client receives events:
    - event: progress, data: {"message": "Starting...", "progress": 0}
    - event: progress, data: {"message": "Inspiration agent...", "progress": 30}  
    - event: progress, data: {"message": "Planning agent...", "progress": 70}
    - event: done, data: {full itinerary result}
    """
    
    # Lazy imports
    from src.travel_lotara.main import run_agent
    from src.travel_lotara.tracking import flush_traces
    
    # Check cache
    request_dict = request.model_dump()
    cache_key = generate_cache_key(request_dict)
    
    cached_result = get_from_cache(cache_key)
    if cached_result:
        async def send_cached():
            yield {
                "event": "cache_hit",
                "data": json.dumps({"message": "Retrieved from cache (instant!)"})
            }
            yield {
                "event": "done",
                "data": json.dumps(cached_result)
            }
        
        return EventSourceResponse(send_cached())
    
    async def event_generator():
        try:
            # Send initial progress
            yield {
                "event": "progress",
                "data": json.dumps({
                    "message": "Starting AI agents...",
                    "progress": 0,
                    "status": "started"
                })
            }
            
            # Progress updates (simulated based on typical execution)
            import asyncio
            
            # Retry configuration
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        yield {
                            "event": "retry",
                            "data": json.dumps({
                                "message": f"Retrying attempt {attempt + 1}/{max_retries}...",
                                "progress": 0,
                                "status": "retrying"
                            })
                        }
                        await asyncio.sleep(2)
                    
                    # Start agent execution
                    agent_task = asyncio.create_task(run_agent(
                        user_input="",
                        user_id=request.userId,
                        backend_json=request_dict,
                    ))
                    
                    # Send progress updates while waiting
                    progress_messages = [
                        (5, "Analyzing your preferences..."),
                        (10, "Inspiration agent starting..."),
                        (30, "Discovering destinations..."),
                        (50, "Planning agent starting..."),
                        (70, "Creating day-by-day itinerary..."),
                        (90, "Finalizing details...")
                    ]
                    
                    progress_idx = 0
                    while not agent_task.done():
                        if progress_idx < len(progress_messages):
                            prog, msg = progress_messages[progress_idx]
                            yield {
                                "event": "progress",
                                "data": json.dumps({
                                    "message": msg,
                                    "progress": prog,
                                    "status": "processing",
                                    "attempt": attempt + 1
                                })
                            }
                            progress_idx += 1
                        await asyncio.sleep(3)  # Update every 3 seconds
                    
                    # Get result
                    response_text, session = await agent_task
                    
                    # Validating response
                    yield {
                        "event": "progress",
                        "data": json.dumps({
                            "message": "Validating itinerary...",
                            "progress": 95,
                            "status": "validating"
                        })
                    }
                    
                    # First, try to get itinerary from session state
                    itinerary_data = None
                    if session and hasattr(session, 'state'):
                        state_itinerary = session.state.get("refactored_itinerary")
                        if state_itinerary and isinstance(state_itinerary, dict):
                            itinerary_data = state_itinerary
                    
                    # If not in state, parse the response text
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
                        itinerary_obj = validation_result.itinerary
                        
                        result = {
                            "status": "completed",
                            "session_id": session.id if session else "unknown",
                            "user_id": request.userId,
                            "itinerary": itinerary_obj,
                            # Extract top-level metadata from itinerary
                            "origin": itinerary_obj.get("origin"),
                            "destination": itinerary_obj.get("destination"),
                            "start_date": itinerary_obj.get("start_date"),
                            "end_date": itinerary_obj.get("end_date"),
                            "itinerary_start_date": itinerary_obj.get("start_date"),
                            "itinerary_end_date": itinerary_obj.get("end_date"),
                            "total_days": int(itinerary_obj.get("total_days", 0)) if itinerary_obj.get("total_days") else None,
                            "average_budget_spend_per_day": itinerary_obj.get("average_budget_spend_per_day"),
                            "average_ratings": itinerary_obj.get("average_ratings"),
                            "error": None
                        }
                        
                        # Cache the result
                        save_to_cache(cache_key, result)
                        
                        # Send completion
                        yield {
                            "event": "done",
                            "data": json.dumps(result)
                        }
                        
                        return  # Success - exit the retry loop
                    else:
                        # Validation failed
                        if attempt < max_retries - 1:
                            yield {
                                "event": "validation_failed",
                                "data": json.dumps({
                                    "message": f"Validation failed, retrying... (attempt {attempt + 1}/{max_retries})",
                                    "errors": validation_result.errors[:3],  # Send first 3 errors
                                    "status": "retrying"
                                })
                            }
                            continue  # Retry
                        else:
                            # Last attempt failed
                            result = {
                                "status": "failed",
                                "session_id": session.id if session else "unknown",
                                "user_id": request.userId,
                                "itinerary": normalized_data,
                                "error": f"Validation failed after {max_retries} attempts. Errors: {'; '.join(validation_result.errors)}"
                            }
                            
                            yield {
                                "event": "error",
                                "data": json.dumps({
                                    "error": "Validation failed",
                                    "message": result["error"],
                                    "details": validation_result.errors
                                })
                            }
                            return
                
                except Exception as e:
                    error_msg = str(e)
                    
                    if attempt < max_retries - 1:
                        yield {
                            "event": "error_retry",
                            "data": json.dumps({
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
                                "error": "Failed to generate itinerary",
                                "details": error_msg[:200]
                            })
                        }
                        return
        
        finally:
            flush_traces()
    
    return EventSourceResponse(event_generator())


@router.get("/cache-status")
async def get_cache_status():
    """Get cache statistics"""
    return {
        "cache_size": len(_cache_storage),
        "cache_limit": 100,
        "message": f"{len(_cache_storage)} itineraries cached in memory"
    }

