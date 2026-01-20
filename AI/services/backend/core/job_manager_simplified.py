"""
Job Manager for Travel Lotara Backend - MVP Simplified Version

Handles async job lifecycle with PostgreSQL:
- Job creation and state management
- Progress tracking
- Partial result accumulation
- Simple polling-based updates (no Redis pubsub)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, AsyncGenerator
from uuid import uuid4

from pydantic import BaseModel

# Note: Add SQLAlchemy imports when integrating with database
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update

logger = logging.getLogger(__name__)


class JobState(BaseModel):
    """Simple job state model."""
    job_id: str
    user_id: str
    status: str  # pending, running, completed, failed
    mode: str
    query: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0


class JobManager:
    """
    Manage job lifecycle with PostgreSQL backend (simplified for MVP).
    
    Features:
    - Async job creation
    - State persistence in PostgreSQL
    - Simple polling-based status updates
    - Automatic cleanup of old jobs
    """
    
    def __init__(self, database_url: str = None):
        """
        Initialize JobManager.
        
        Args:
            database_url: PostgreSQL connection URL (optional, uses env var if not provided)
        """
        self.database_url = database_url
        # TODO: Initialize SQLAlchemy engine and session factory
        self._jobs: dict[str, JobState] = {}  # In-memory fallback for MVP
        
        # TTLs
        self.JOB_TTL_HOURS = 24  # Keep jobs for 24 hours
    
    async def connect(self):
        """Initialize database connection."""
        # TODO: Set up SQLAlchemy async engine
        logger.info("JobManager initialized (using in-memory storage for MVP)")
    
    async def close(self):
        """Close database connection."""
        # TODO: Close SQLAlchemy engine
        logger.info("JobManager closed")
    
    # ============================================
    # JOB LIFECYCLE
    # ============================================
    
    async def create_job(
        self,
        user_id: str,
        mode: str,
        query: Optional[str] = None,
        constraints: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Create a new job.
        
        Args:
            user_id: User identifier
            mode: Workflow mode (planning, booking, etc.)
            query: User query/request
            constraints: Additional constraints
            
        Returns:
            job_id: Unique job identifier
        """
        job_id = str(uuid4())
        now = datetime.utcnow()
        
        job_state = JobState(
            job_id=job_id,
            user_id=user_id,
            status="pending",
            mode=mode,
            query=query,
            created_at=now,
            updated_at=now,
        )
        
        # Store in memory (TODO: save to PostgreSQL)
        self._jobs[job_id] = job_state
        
        logger.info(f"Created job {job_id} for user {user_id}")
        return job_id
    
    async def get_job(self, job_id: str) -> Optional[JobState]:
        """Get job state by ID."""
        # TODO: Query from PostgreSQL
        return self._jobs.get(job_id)
    
    async def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        progress: Optional[float] = None,
    ):
        """
        Update job status.
        
        Args:
            job_id: Job identifier
            status: New status (running, completed, failed)
            result: Job result data
            error: Error message if failed
            progress: Progress percentage (0.0 to 1.0)
        """
        job = self._jobs.get(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return
        
        job.status = status
        job.updated_at = datetime.utcnow()
        
        if result is not None:
            job.result = result
        if error is not None:
            job.error = error
        if progress is not None:
            job.progress = progress
        
        # TODO: Update in PostgreSQL
        logger.debug(f"Updated job {job_id}: status={status}, progress={progress}")
    
    async def list_user_jobs(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[JobState]:
        """
        List jobs for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of jobs to return
            offset: Pagination offset
            
        Returns:
            List of job states
        """
        # TODO: Query from PostgreSQL with pagination
        user_jobs = [
            job for job in self._jobs.values()
            if job.user_id == user_id
        ]
        
        # Sort by created_at descending
        user_jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        return user_jobs[offset:offset + limit]
    
    async def cleanup_old_jobs(self):
        """Remove jobs older than TTL."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.JOB_TTL_HOURS)
        
        # TODO: Delete from PostgreSQL
        jobs_to_remove = [
            job_id for job_id, job in self._jobs.items()
            if job.created_at < cutoff_time
        ]
        
        for job_id in jobs_to_remove:
            del self._jobs[job_id]
            
        if jobs_to_remove:
            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    async def get_job_result(self, job_id: str) -> Optional[dict[str, Any]]:
        """Get the final result of a completed job."""
        job = await self.get_job(job_id)
        if job and job.status == "completed":
            return job.result
        return None
    
    async def wait_for_completion(
        self,
        job_id: str,
        timeout: float = 300,
        poll_interval: float = 1.0,
    ) -> JobState:
        """
        Wait for job to complete (polling-based).
        
        Args:
            job_id: Job identifier
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            Final job state
            
        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            job = await self.get_job(job_id)
            
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            if job.status in ["completed", "failed"]:
                return job
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
            
            await asyncio.sleep(poll_interval)


# Example usage
if __name__ == "__main__":
    async def test():
        manager = JobManager()
        await manager.connect()
        
        # Create job
        job_id = await manager.create_job(
            user_id="user123",
            mode="planning",
            query="Plan a trip to Paris",
        )
        
        # Update progress
        await manager.update_job_status(job_id, "running", progress=0.5)
        
        # Complete job
        await manager.update_job_status(
            job_id,
            "completed",
            result={"itinerary": "..."},
            progress=1.0,
        )
        
        # Get result
        job = await manager.get_job(job_id)
        print(f"Job status: {job.status}")
        print(f"Result: {job.result}")
        
        await manager.close()
    
    asyncio.run(test())
