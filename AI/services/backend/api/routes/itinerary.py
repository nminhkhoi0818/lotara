"""Itinerary generation endpoint."""

import sys
import os
import json
import time
from fastapi import APIRouter, HTTPException
from api.models import ItineraryRequest, ItineraryResponse

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.travel_lotara.main import run_agent
from src.travel_lotara.tracking import flush_traces
from api.middleware.rate_limiter import request_queue

router = APIRouter(prefix="/api/itinerary", tags=["itinerary"])


@router.get("/queue-status")
async def get_queue_status():
    """Get current request queue status."""
    return request_queue.get_queue_status()


@router.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    """
    Generate a personalized travel itinerary using AI agents.
    
    This endpoint accepts user preferences and generates a complete
    day-by-day itinerary including transport, accommodation, and activities.
    
    The request may take 30-120 seconds to process as multiple AI agents
    work together to create a comprehensive travel plan.
    
    Note: Requests are queued to prevent API rate limiting.
    Check /api/itinerary/queue-status for current queue status.
    """
    
    # Acquire queue slot (will wait if queue is full)
    queue_start = time.time()
    await request_queue.acquire()
    queue_wait = time.time() - queue_start
    
    if queue_wait > 1:
        print(f"[QUEUE] Request waited {queue_wait:.1f}s in queue")
    
    try:
        # Convert request to dict for agent processing
        backend_json = request.model_dump()
        
        # Run the agent system
        response_text, session = await run_agent(
            user_input="",
            user_id=request.userId,
            backend_json=backend_json,
        )
        
        # Parse the response (agent returns JSON string)
        try:
            itinerary_data = json.loads(response_text)
        except json.JSONDecodeError:
            # If response is not JSON, wrap it
            itinerary_data = {
                "raw_response": response_text,
                "note": "Response was not in expected JSON format"
            }
        
        return ItineraryResponse(
            status="completed",
            session_id=session.id,
            user_id=request.userId,
            itinerary=itinerary_data,
            error=None
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's a retryable error
        if "503" in error_msg or "overloaded" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "ServiceUnavailable",
                    "message": "AI service is temporarily overloaded. Please try again in a few minutes.",
                    "details": error_msg[:200],
                    "retry_after": 120  # Suggest retry after 2 minutes
                }
            )
        elif "429" in error_msg or "rate limit" in error_msg.lower() or "resource_exhausted" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "RateLimitExceeded",
                    "message": "Google Gemini API rate limit exceeded. Please wait 5-10 minutes and try again.",
                    "details": error_msg[:200],
                    "suggestions": [
                        "Wait 5-10 minutes before retrying",
                        "Check API quota at https://aistudio.google.com/app/apikey",
                        "Consider switching to gemini-1.5-flash model (less rate limited)",
                        "Current requests are queued to prevent overload"
                    ],
                    "retry_after": 300  # Suggest retry after 5 minutes
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "InternalServerError",
                    "message": "Failed to generate itinerary",
                    "details": error_msg[:200]
                }
            )
    
    finally:
        # Always release queue slot and flush traces
        request_queue.release()
        flush_traces()
