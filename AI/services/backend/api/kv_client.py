"""
Vercel KV client for job queue and caching
"""
import os
import json
import hashlib
from typing import Optional, Dict, Any
from redis import Redis
from datetime import datetime, timedelta

class VercelKV:
    """Client for Vercel KV (Redis) storage"""
    
    def __init__(self):
        """Initialize Redis connection from environment variables"""
        kv_url = os.getenv("KV_REST_API_URL")
        kv_token = os.getenv("KV_REST_API_TOKEN")
        
        if not kv_url or not kv_token:
            # Fallback to local Redis for development
            self.client = Redis(host='localhost', port=6379, decode_responses=True)
            self.is_local = True
        else:
            # Vercel KV connection (REST API compatible)
            self.client = Redis.from_url(
                kv_url,
                password=kv_token,
                decode_responses=True
            )
            self.is_local = False
    
    # Job Queue Operations
    
    def create_job(self, job_id: str, request_data: Dict[str, Any]) -> None:
        """Create a new job in the queue"""
        job_data = {
            "id": job_id,
            "status": "pending",
            "request": request_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "progress": 0
        }
        self.client.setex(
            f"job:{job_id}",
            timedelta(days=7),  # Jobs expire after 7 days
            json.dumps(job_data)
        )
        # Add to pending queue
        self.client.rpush("queue:pending", job_id)
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and results"""
        data = self.client.get(f"job:{job_id}")
        if data:
            return json.loads(data)
        return None
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> None:
        """Update job status/progress/results"""
        job = self.get_job(job_id)
        if job:
            job.update(updates)
            job["updated_at"] = datetime.utcnow().isoformat()
            self.client.setex(
                f"job:{job_id}",
                timedelta(days=7),
                json.dumps(job)
            )
    
    def get_pending_jobs(self, limit: int = 10) -> list[str]:
        """Get pending job IDs from queue"""
        job_ids = []
        for _ in range(limit):
            job_id = self.client.lpop("queue:pending")
            if not job_id:
                break
            job_ids.append(job_id)
        return job_ids
    
    # Cache Operations
    
    def generate_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Generate cache key from request parameters"""
        # Sort keys for consistent hashing
        cache_string = json.dumps(request_data, sort_keys=True)
        return f"cache:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached itinerary result"""
        data = self.client.get(cache_key)
        if data:
            return json.loads(data)
        return None
    
    def set_cached_result(self, cache_key: str, result: Dict[str, Any], ttl_days: int = 30) -> None:
        """Cache itinerary result"""
        self.client.setex(
            cache_key,
            timedelta(days=ttl_days),
            json.dumps(result)
        )
    
    # Utility
    
    def ping(self) -> bool:
        """Check if KV is accessible"""
        try:
            self.client.ping()
            return True
        except Exception:
            return False

# Global instance
kv_client = VercelKV()
