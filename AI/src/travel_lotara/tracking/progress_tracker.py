"""
Real-time progress tracking for AI agent execution.

This module provides a thread-safe progress tracking system that captures
agent thinking, tool calls, and model responses to stream to frontend clients.
"""

import asyncio
import time
from typing import Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque


class ProgressEventType(str, Enum):
    """Types of progress events that can be tracked"""
    STARTED = "started"
    AGENT_STARTED = "agent_started"
    AGENT_THINKING = "agent_thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    MODEL_CALL = "model_call"
    MODEL_RESPONSE = "model_response"
    VALIDATION = "validation"
    COMPLETED = "completed"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ProgressEvent:
    """A single progress event"""
    type: ProgressEventType
    message: str
    progress: int  # 0-100
    timestamp: float
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['type'] = self.type.value
        return data


class ProgressTracker:
    """
    Thread-safe progress tracker for streaming agent execution updates.
    
    Usage:
        # In endpoint:
        tracker = ProgressTracker(session_id="abc123")
        
        # In callbacks:
        tracker.add_event("agent_started", "Inspiration Agent starting...", 20)
        
        # Stream to client:
        async for event in tracker.stream_events():
            yield event
    """
    
    # Global registry of trackers by session_id
    _trackers: Dict[str, "ProgressTracker"] = {}
    _lock = asyncio.Lock()
    
    def __init__(self, session_id: str, max_events: int = 100):
        """
        Initialize progress tracker for a session.
        
        Args:
            session_id: Unique session identifier
            max_events: Maximum number of events to buffer
        """
        self.session_id = session_id
        self.max_events = max_events
        self.events: deque[ProgressEvent] = deque(maxlen=max_events)
        self.current_progress = 0
        self.is_complete = False
        self.error: Optional[str] = None
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._created_at = time.time()
        
    @classmethod
    async def get_tracker(cls, session_id: str) -> "ProgressTracker":
        """Get or create a tracker for a session (async-safe)"""
        async with cls._lock:
            if session_id not in cls._trackers:
                cls._trackers[session_id] = ProgressTracker(session_id)
            return cls._trackers[session_id]
    
    @classmethod
    async def remove_tracker(cls, session_id: str):
        """Remove tracker after completion (async-safe)"""
        async with cls._lock:
            if session_id in cls._trackers:
                del cls._trackers[session_id]
    
    @classmethod
    def get_tracker_sync(cls, session_id: str) -> "ProgressTracker":
        """Get or create tracker (synchronous - for use in callbacks)"""
        if session_id not in cls._trackers:
            cls._trackers[session_id] = ProgressTracker(session_id)
        return cls._trackers[session_id]
    
    def add_event(
        self,
        event_type: ProgressEventType | str,
        message: str,
        progress: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Add a progress event (thread-safe).
        
        Args:
            event_type: Type of event (ProgressEventType or string)
            message: Human-readable message
            progress: Progress percentage (0-100), auto-increments if None
            details: Additional event metadata
        """
        if isinstance(event_type, str):
            try:
                event_type = ProgressEventType(event_type)
            except ValueError:
                event_type = ProgressEventType.AGENT_THINKING
        
        # Auto-increment progress if not specified
        if progress is None:
            progress = min(self.current_progress + 5, 95)  # Never reach 100 automatically
        
        self.current_progress = progress
        
        event = ProgressEvent(
            type=event_type,
            message=message,
            progress=progress,
            timestamp=time.time(),
            details=details or {}
        )
        
        self.events.append(event)
        
        # Try to add to async queue (non-blocking)
        try:
            self._event_queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # Queue full, skip this event
    
    def mark_complete(self, message: str = "Itinerary generation complete!"):
        """Mark the process as complete"""
        self.is_complete = True
        self.add_event(
            ProgressEventType.COMPLETED,
            message,
            progress=100
        )
    
    def mark_error(self, error_message: str):
        """Mark the process as failed"""
        self.error = error_message
        self.is_complete = True
        self.add_event(
            ProgressEventType.ERROR,
            f"Error: {error_message}",
            progress=self.current_progress
        )
    
    async def stream_events(self, timeout: float = 120.0) -> AsyncGenerator[ProgressEvent, None]:
        """
        Stream events as they occur (async generator).
        
        Args:
            timeout: Maximum time to wait for completion (seconds)
            
        Yields:
            ProgressEvent objects as they're added
        """
        start_time = time.time()
        
        while not self.is_complete:
            try:
                # Wait for next event with short timeout
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=2.0
                )
                yield event
                
            except asyncio.TimeoutError:
                # No event in 2 seconds, check if we should timeout
                if time.time() - start_time > timeout:
                    self.mark_error(f"Timeout after {timeout}s")
                    break
                continue
        
        # Send any final events
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                yield event
            except asyncio.QueueEmpty:
                break
    
    def get_recent_events(self, limit: int = 10) -> list[ProgressEvent]:
        """Get the most recent events"""
        events_list = list(self.events)
        return events_list[-limit:] if len(events_list) > limit else events_list
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status summary"""
        return {
            "session_id": self.session_id,
            "progress": self.current_progress,
            "is_complete": self.is_complete,
            "error": self.error,
            "total_events": len(self.events),
            "elapsed_time": time.time() - self._created_at,
            "recent_message": self.events[-1].message if self.events else "Starting..."
        }


# Helper functions for common progress updates

def track_agent_start(session_id: str, agent_name: str, progress: int):
    """Helper to track agent start"""
    tracker = ProgressTracker.get_tracker_sync(session_id)
    tracker.add_event(
        ProgressEventType.AGENT_STARTED,
        f"🤖 {agent_name} starting...",
        progress=progress,
        details={"agent": agent_name}
    )


def track_tool_call(session_id: str, tool_name: str, args: Dict[str, Any]):
    """Helper to track tool invocation"""
    tracker = ProgressTracker.get_tracker_sync(session_id)
    
    # Create user-friendly message based on tool type
    if "chromadb" in tool_name.lower() or "rag" in tool_name.lower():
        location = args.get("location", args.get("city", "locations"))
        message = f"🔍 Searching database for {location}..."
    elif "search" in tool_name.lower():
        query = args.get("query", "information")[:50]
        message = f"🌐 Searching for: {query}..."
    else:
        message = f"🛠️ Using {tool_name}..."
    
    tracker.add_event(
        ProgressEventType.TOOL_CALL,
        message,
        details={"tool": tool_name, "args": args}
    )


def track_tool_result(session_id: str, tool_name: str, result_summary: str):
    """Helper to track tool result"""
    tracker = ProgressTracker.get_tracker_sync(session_id)
    tracker.add_event(
        ProgressEventType.TOOL_RESULT,
        f"✅ {result_summary}",
        details={"tool": tool_name}
    )


def track_model_call(session_id: str, model_name: str, purpose: str):
    """Helper to track LLM call"""
    tracker = ProgressTracker.get_tracker_sync(session_id)
    tracker.add_event(
        ProgressEventType.MODEL_CALL,
        f"💭 {purpose}...",
        details={"model": model_name}
    )


def track_thinking(session_id: str, message: str, progress: Optional[int] = None):
    """Helper to track general thinking/processing"""
    tracker = ProgressTracker.get_tracker_sync(session_id)
    tracker.add_event(
        ProgressEventType.AGENT_THINKING,
        message,
        progress=progress
    )
