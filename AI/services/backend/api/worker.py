"""
Background worker for processing itinerary generation jobs
This runs as a separate Vercel serverless function with 300s timeout
"""
import sys
import os
import json
import asyncio
from datetime import datetime

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))

from services.backend.api.kv_client import kv_client


async def process_single_job(job_id: str) -> dict:
    """Process a single job"""
    from src.travel_lotara.main import run_agent
    from src.travel_lotara.tracking import flush_traces
    
    print(f"[WORKER] Processing job {job_id}")
    
    job = kv_client.get_job(job_id)
    if not job:
        print(f"[WORKER] Job {job_id} not found")
        return {"error": "Job not found"}
    
    try:
        # Update status to processing
        kv_client.update_job(job_id, {
            "status": "processing",
            "progress": 10,
            "message": "Starting AI agents..."
        })
        
        request_data = job["request"]
        print(f"[WORKER] Job {job_id} - Running agents for {request_data.get('destination', 'unknown')}")
        
        # Update progress - pre-agent starting
        kv_client.update_job(job_id, {
            "progress": 20,
            "message": "Pre-agent optimizing request..."
        })
        
        # Run the agent system
        response_text, session = await run_agent(
            user_input="",
            user_id=request_data.get("userId", "worker"),
            backend_json=request_data,
        )
        
        # Update progress - inspiration agent
        kv_client.update_job(job_id, {
            "progress": 50,
            "message": "Inspiration agent generating concepts..."
        })
        
        # Update progress - planning agent
        kv_client.update_job(job_id, {
            "progress": 80,
            "message": "Planning agent creating detailed itinerary..."
        })
        
        # Parse the response
        try:
            itinerary_data = json.loads(response_text)
        except json.JSONDecodeError:
            itinerary_data = {
                "raw_response": response_text,
                "note": "Response was not in expected JSON format"
            }
        
        # Build result
        result = {
            "status": "completed",
            "session_id": session.id,
            "user_id": request_data.get("userId"),
            "itinerary": itinerary_data,
            "error": None
        }
        
        # Update job as completed
        kv_client.update_job(job_id, {
            "status": "completed",
            "progress": 100,
            "result": result,
            "message": "Itinerary generation completed successfully"
        })
        
        # Cache the result
        cache_key = kv_client.generate_cache_key(request_data)
        kv_client.set_cached_result(cache_key, {
            "job_id": job_id,
            **result
        }, ttl_days=30)
        
        print(f"[WORKER] Job {job_id} completed successfully")
        
        # Flush traces
        flush_traces()
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"[WORKER] Job {job_id} failed: {error_msg[:200]}")
        
        # Update job as failed
        kv_client.update_job(job_id, {
            "status": "failed",
            "progress": 0,
            "error": error_msg[:500],
            "message": f"Job failed: {error_msg[:100]}"
        })
        
        return {"error": error_msg}


async def process_jobs(max_jobs: int = 10):
    """Process pending jobs from the queue"""
    print(f"[WORKER] Starting job processor (max {max_jobs} jobs)")
    
    # Get pending jobs
    job_ids = kv_client.get_pending_jobs(limit=max_jobs)
    
    if not job_ids:
        print("[WORKER] No pending jobs in queue")
        return {
            "processed": 0,
            "message": "No jobs to process"
        }
    
    print(f"[WORKER] Found {len(job_ids)} pending jobs")
    
    # Process jobs sequentially (Gemini API rate limits prevent parallelism)
    results = []
    for job_id in job_ids:
        try:
            result = await process_single_job(job_id)
            results.append({
                "job_id": job_id,
                "status": "success" if "error" not in result else "failed"
            })
        except Exception as e:
            print(f"[WORKER] Error processing job {job_id}: {str(e)}")
            results.append({
                "job_id": job_id,
                "status": "error",
                "error": str(e)[:200]
            })
    
    print(f"[WORKER] Processed {len(results)} jobs")
    
    return {
        "processed": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


# Vercel serverless function handler
def handler(event, context):
    """
    Vercel cron job handler
    
    Setup in Vercel dashboard:
    1. Go to Project Settings > Cron Jobs
    2. Add: /api/process-jobs with schedule */1 * * * * (every minute)
    """
    print("[WORKER] Cron job triggered")
    
    # Run async job processor
    result = asyncio.run(process_jobs(max_jobs=5))
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }


# For manual testing
if __name__ == "__main__":
    print("Running worker manually...")
    result = asyncio.run(process_jobs(max_jobs=10))
    print(json.dumps(result, indent=2))
