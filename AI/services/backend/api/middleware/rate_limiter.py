"""Rate limiting and request queue management."""

import asyncio
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Optional


class RequestQueue:
    """
    Simple request queue to prevent overwhelming the API.
    Implements a semaphore-based rate limiter with queue.
    """
    
    def __init__(self, max_concurrent: int = 2, requests_per_minute: int = 5):
        """
        Initialize request queue.
        
        Args:
            max_concurrent: Maximum concurrent requests allowed
            requests_per_minute: Maximum requests per minute allowed
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.requests_per_minute = requests_per_minute
        self.request_times: deque = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        # Wait for semaphore (concurrent limit)
        await self.semaphore.acquire()
        
        # Check rate limit
        async with self.lock:
            now = datetime.now()
            
            # Remove old requests (older than 1 minute)
            cutoff = now - timedelta(minutes=1)
            while self.request_times and self.request_times[0] < cutoff:
                self.request_times.popleft()
            
            # Check if we're at the rate limit
            if len(self.request_times) >= self.requests_per_minute:
                # Calculate wait time until oldest request expires
                oldest = self.request_times[0]
                wait_until = oldest + timedelta(minutes=1)
                wait_seconds = (wait_until - now).total_seconds()
                
                if wait_seconds > 0:
                    print(f"[RATE LIMIT] Queue full, waiting {wait_seconds:.1f}s...")
                    await asyncio.sleep(wait_seconds)
            
            # Record this request
            self.request_times.append(datetime.now())
    
    def release(self):
        """Release the semaphore."""
        self.semaphore.release()
    
    def get_queue_status(self) -> dict:
        """Get current queue status."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Count recent requests
        recent_count = sum(1 for t in self.request_times if t > cutoff)
        
        return {
            "available_slots": self.semaphore._value,
            "max_concurrent": self.semaphore._value + (2 - self.semaphore._value),  # Total slots
            "requests_last_minute": recent_count,
            "requests_per_minute_limit": self.requests_per_minute,
            "queue_utilization": f"{(recent_count / self.requests_per_minute) * 100:.1f}%"
        }


# Global request queue instance
# Adjust these values based on your API quota
request_queue = RequestQueue(
    max_concurrent=2,  # Only 2 concurrent itinerary generations
    requests_per_minute=3  # Conservative limit to avoid 429
)
