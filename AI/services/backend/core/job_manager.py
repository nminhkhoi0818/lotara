"""
Job Manager for Travel Lotara Backend

Handles async job lifecycle with Redis:
- Job creation and state management
- Progress tracking
- Partial result accumulation
- Event publishing for SSE
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, AsyncGenerator
from uuid import uuid4

from pydantic import BaseModel

try:
    import redis.asyncio as aioredis
except ImportError:
    raise ImportError("Install redis: pip install redis[async]")

from .models import (
    JobState,
    JobStatus,
    WorkflowMode,
    StreamEvent,
    EventType,
    TaskInfo,
)


logger = logging.getLogger(__name__)


class JobManager:
    """
    Manage job lifecycle with Redis backend.
    
    Features:
    - Async job creation
    - State persistence
    - Event streaming
    - TTL-based cleanup
    - Atomic updates
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize JobManager.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self._pubsub_tasks: dict[str, asyncio.Task] = {}
        
        # Key prefixes
        self.JOB_PREFIX = "job:"
        self.EVENTS_PREFIX = "events:"
        
        # TTLs
        self.JOB_TTL = 86400  # 24 hours
        self.EVENTS_TTL = 3600  # 1 hour
    
    async def connect(self):
        """Establish Redis connection."""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
            logger.info("JobManager connected to Redis")
    
    async def close(self):
        """Close Redis connection."""
        # Cancel all pubsub tasks
        for task in self._pubsub_tasks.values():
            task.cancel()
        
        if self.redis:
            await self.redis.close()
            logger.info("JobManager disconnected from Redis")
    
    # ============================================
    # JOB LIFECYCLE
    # ============================================
    
    async def create_job(
        self,
        user_id: str,
        mode: WorkflowMode,
        query: Optional[str] = None,
        constraints: Optional[dict[str, Any]] = None,
        trigger_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Create new job.
        
        Args:
            user_id: User identifier
            mode: reactive or proactive
            query: User query (reactive mode)
            constraints: User constraints
            trigger_context: Trigger data (proactive mode)
        
        Returns:
            job_id
        """
        job_id = str(uuid4())
        
        state = JobState(
            job_id=job_id,
            user_id=user_id,
            mode=mode,
            query=query,
            constraints=constraints or {},
            trigger_context=trigger_context,
        )
        
        await self._save_job(state)
        
        logger.info(f"Created job {job_id} for user {user_id} ({mode.value} mode)")
        
        # Publish creation event
        await self._publish_event(
            job_id,
            EventType.STATE_CHANGE,
            {
                "status": JobStatus.STARTED.value,
                "mode": mode.value,
            }
        )
        
        return job_id
    
    async def get_job(self, job_id: str) -> Optional[JobState]:
        """
        Retrieve job state.
        
        Args:
            job_id: Job identifier
        
        Returns:
            JobState if found, None otherwise
        """
        key = f"{self.JOB_PREFIX}{job_id}"
        data = await self.redis.get(key)
        
        if not data:
            return None
        
        return JobState.model_validate_json(data)
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        error: Optional[dict[str, Any]] = None,
    ):
        """
        Update job status.
        
        Args:
            job_id: Job identifier
            status: New status
            error: Error details if failed
        """
        state = await self.get_job(job_id)
        if not state:
            raise ValueError(f"Job {job_id} not found")
        
        state.status = status
        state.updated_at = datetime.utcnow()
        
        if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            state.completed_at = datetime.utcnow()
        
        if error:
            state.error = error
        
        await self._save_job(state)
        
        # Publish status change
        await self._publish_event(
            job_id,
            EventType.STATE_CHANGE,
            {
                "status": status.value,
                "error": error,
            }
        )
    
    async def update_workflow_state(
        self,
        job_id: str,
        workflow_state: str,
    ):
        """
        Update workflow state (monitoring, intake, planning, etc).
        
        Args:
            job_id: Job identifier
            workflow_state: Current workflow state
        """
        state = await self.get_job(job_id)
        if not state:
            raise ValueError(f"Job {job_id} not found")
        
        state.current_state = workflow_state
        state.updated_at = datetime.utcnow()
        
        await self._save_job(state)
        
        # Publish state change
        await self._publish_event(
            job_id,
            EventType.STATE_CHANGE,
            {"workflow_state": workflow_state}
        )
    
    async def add_task_result(
        self,
        job_id: str,
        task_info: TaskInfo,
    ):
        """
        Add or update task result.
        
        Args:
            job_id: Job identifier
            task_info: Task execution info
        """
        state = await self.get_job(job_id)
        if not state:
            raise ValueError(f"Job {job_id} not found")
        
        # Update or append task
        existing_idx = next(
            (i for i, t in enumerate(state.tasks) if t.task_id == task_info.task_id),
            None
        )
        
        if existing_idx is not None:
            state.tasks[existing_idx] = task_info
        else:
            state.tasks.append(task_info)
        
        state.updated_at = datetime.utcnow()
        
        await self._save_job(state)
        
        # Publish task event
        event_type = (
            EventType.TASK_COMPLETE
            if task_info.status == "completed"
            else EventType.TASK_START
        )
        
        await self._publish_event(
            job_id,
            event_type,
            {
                "task_id": task_info.task_id,
                "agent": task_info.agent,
                "task_name": task_info.task_name,
                "status": task_info.status,
                "output": task_info.output,
                "confidence_score": task_info.confidence_score,
            }
        )
    
    async def update_partial_output(
        self,
        job_id: str,
        key: str,
        value: Any,
    ):
        """
        Update partial output (for streaming).
        
        Args:
            job_id: Job identifier
            key: Output key (e.g., "flights", "hotels")
            value: Output value
        """
        state = await self.get_job(job_id)
        if not state:
            raise ValueError(f"Job {job_id} not found")
        
        state.partial_outputs[key] = value
        state.updated_at = datetime.utcnow()
        
        await self._save_job(state)
        
        # Publish agent output
        await self._publish_event(
            job_id,
            EventType.AGENT_OUTPUT,
            {
                "key": key,
                "value": value,
            }
        )
    
    async def set_final_result(
        self,
        job_id: str,
        result: dict[str, Any],
    ):
        """
        Set final result and mark completed.
        
        Args:
            job_id: Job identifier
            result: Complete itinerary
        """
        state = await self.get_job(job_id)
        if not state:
            raise ValueError(f"Job {job_id} not found")
        
        state.final_result = result
        state.status = JobStatus.COMPLETED
        state.completed_at = datetime.utcnow()
        state.updated_at = datetime.utcnow()
        
        await self._save_job(state)
        
        # Publish completion
        await self._publish_event(
            job_id,
            EventType.COMPLETE,
            {"result": result}
        )
    
    async def request_approval(
        self,
        job_id: str,
        approval_data: dict[str, Any],
    ):
        """
        Request human-in-the-loop approval.
        
        Args:
            job_id: Job identifier
            approval_data: What needs approval
        """
        state = await self.get_job(job_id)
        if not state:
            raise ValueError(f"Job {job_id} not found")
        
        state.status = JobStatus.WAITING_APPROVAL
        state.awaiting_approval = True
        state.approval_data = approval_data
        state.updated_at = datetime.utcnow()
        
        await self._save_job(state)
        
        # Publish approval request
        await self._publish_event(
            job_id,
            EventType.STATE_CHANGE,
            {
                "status": JobStatus.WAITING_APPROVAL.value,
                "approval_data": approval_data,
            }
        )
    
    async def set_opik_trace(
        self,
        job_id: str,
        trace_id: str,
        trace_url: str,
    ):
        """
        Associate Opik trace with job.
        
        Args:
            job_id: Job identifier
            trace_id: Opik trace ID
            trace_url: Opik trace URL
        """
        state = await self.get_job(job_id)
        if not state:
            raise ValueError(f"Job {job_id} not found")
        
        state.opik_trace_id = trace_id
        state.opik_trace_url = trace_url
        state.updated_at = datetime.utcnow()
        
        await self._save_job(state)
    
    # ============================================
    # EVENT STREAMING
    # ============================================
    
    async def stream_events(
        self,
        job_id: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream events for a job (SSE).
        
        Args:
            job_id: Job identifier
        
        Yields:
            StreamEvent objects
        """
        # Subscribe to job events
        pubsub = self.redis.pubsub()
        channel = f"{self.EVENTS_PREFIX}{job_id}"
        
        await pubsub.subscribe(channel)
        
        try:
            # Send current state first
            state = await self.get_job(job_id)
            if state:
                yield StreamEvent(
                    event_type=EventType.STATE_CHANGE,
                    data={
                        "status": state.status.value,
                        "current_state": state.current_state,
                    }
                )
            
            # Stream future events
            async for message in pubsub.listen():
                if message["type"] == "message":
                    event_data = json.loads(message["data"])
                    event = StreamEvent(
                        event_type=EventType(event_data["event_type"]),
                        data=event_data["data"],
                    )
                    yield event
                    
                    # Stop streaming if job complete/failed
                    if event.event_type == EventType.COMPLETE:
                        break
                    if event.event_type == EventType.ERROR:
                        break
        
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
    
    # ============================================
    # INTERNAL HELPERS
    # ============================================
    
    async def _save_job(self, state: JobState):
        """Save job state to Redis."""
        key = f"{self.JOB_PREFIX}{state.job_id}"
        await self.redis.setex(
            key,
            self.JOB_TTL,
            state.model_dump_json(),
        )
    
    async def _publish_event(
        self,
        job_id: str,
        event_type: EventType,
        data: dict[str, Any],
    ):
        """Publish event to job's channel."""
        channel = f"{self.EVENTS_PREFIX}{job_id}"
        
        event_data = {
            "event_type": event_type.value,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.redis.publish(
            channel,
            json.dumps(event_data, default=str)
        )
    
    # ============================================
    # CLEANUP
    # ============================================
    
    async def cleanup_old_jobs(self, older_than_hours: int = 24):
        """
        Clean up old jobs.
        
        Args:
            older_than_hours: Delete jobs older than this
        """
        # Redis EXPIRE handles this automatically with TTL
        # This is just for manual cleanup if needed
        pass
