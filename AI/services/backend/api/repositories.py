"""
Repository Classes for Vercel Serverless Database Operations.

Stateless repository pattern optimized for serverless functions.
Uses Supabase for all database operations.
"""

from __future__ import annotations

import os
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _get_supabase_client():
    """Get Supabase client for repository operations."""
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if url and key:
            return create_client(url, key)
    except Exception as e:
        logger.warning(f"Supabase not available: {e}")
    return None


class JobRepository:
    """Repository for job records."""
    
    def __init__(self):
        self.table_name = "jobs"
    
    @property
    def client(self):
        return _get_supabase_client()
    
    @property
    def table(self):
        return self.client.table(self.table_name) if self.client else None
    
    def create(self, job):
        """Create a new job record."""
        from models import JobRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        data = job.model_dump(mode="json")
        response = self.table.insert(data).execute()
        
        if response.data:
            logger.info(f"Created job: {job.id}")
            return JobRecord(**response.data[0])
        raise RuntimeError("Failed to create job record")
    
    def get_by_id(self, job_id: str):
        """Get a job by ID."""
        from models import JobRecord
        
        if not self.table:
            return None
        
        response = (
            self.table
            .select("*")
            .eq("id", job_id)
            .maybe_single()
            .execute()
        )
        
        if response.data:
            return JobRecord(**response.data)
        return None
    
    def get_by_user(self, user_id: str, limit: int = 10, status=None):
        """Get jobs for a user."""
        from models import JobRecord
        
        if not self.table:
            return []
        
        query = (
            self.table
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
        )
        
        if status:
            query = query.eq("status", status.value)
        
        response = query.execute()
        return [JobRecord(**record) for record in response.data]
    
    def update(self, job_id: str, updates: dict[str, Any]):
        """Update a job record."""
        from models import JobRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        response = (
            self.table
            .update(updates)
            .eq("id", job_id)
            .execute()
        )
        
        if response.data:
            logger.info(f"Updated job: {job_id}")
            return JobRecord(**response.data[0])
        raise RuntimeError(f"Job {job_id} not found")
    
    def update_status(self, job_id: str, status, partial_outputs=None, error=None):
        """Update job status with optional outputs."""
        updates = {"status": status.value}
        
        if partial_outputs:
            updates["partial_outputs"] = partial_outputs
        
        if error:
            updates["error"] = error
        
        from models import JobStatus
        if status == JobStatus.COMPLETED:
            updates["completed_at"] = datetime.utcnow().isoformat()
        
        return self.update(job_id, updates)


class SessionRepository:
    """Repository for session records."""
    
    def __init__(self):
        self.table_name = "sessions"
    
    @property
    def client(self):
        return _get_supabase_client()
    
    @property
    def table(self):
        return self.client.table(self.table_name) if self.client else None
    
    def create(self, session):
        """Create a new session."""
        from models import SessionRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        data = session.model_dump(mode="json")
        response = self.table.insert(data).execute()
        
        if response.data:
            return SessionRecord(**response.data[0])
        raise RuntimeError("Failed to create session")
    
    def get_by_id(self, session_id: str):
        """Get session by ID."""
        from models import SessionRecord
        
        if not self.table:
            return None
        
        response = (
            self.table
            .select("*")
            .eq("id", session_id)
            .maybe_single()
            .execute()
        )
        
        if response.data:
            return SessionRecord(**response.data)
        return None
    
    def get_active_session(self, user_id: str):
        """Get user's current active session."""
        from models import SessionRecord
        
        if not self.table:
            return None
        
        response = (
            self.table
            .select("*")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .order("last_activity_at", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )
        
        if response.data:
            return SessionRecord(**response.data)
        return None
    
    def update(self, session_id: str, updates: dict[str, Any]):
        """Update a session."""
        from models import SessionRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        updates["updated_at"] = datetime.utcnow().isoformat()
        updates["last_activity_at"] = datetime.utcnow().isoformat()
        
        response = (
            self.table
            .update(updates)
            .eq("id", session_id)
            .execute()
        )
        
        if response.data:
            return SessionRecord(**response.data[0])
        raise RuntimeError(f"Session {session_id} not found")
    
    def add_message(self, session_id: str, role: str, content: str, metadata=None):
        """Add a message to session history."""
        session = self.get_by_id(session_id)
        if not session:
            raise RuntimeError(f"Session {session_id} not found")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Keep only last 50 messages (optimize for free tier)
        messages = session.messages[-49:] + [message]
        
        return self.update(session_id, {"messages": messages})


class FeedbackRepository:
    """Repository for feedback records."""
    
    def __init__(self):
        self.table_name = "feedback"
    
    @property
    def client(self):
        return _get_supabase_client()
    
    @property
    def table(self):
        return self.client.table(self.table_name) if self.client else None
    
    def create(self, feedback):
        """Create a feedback record."""
        from models import FeedbackRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        data = feedback.model_dump(mode="json")
        response = self.table.insert(data).execute()
        
        if response.data:
            logger.info(f"Created feedback: {feedback.id}")
            return FeedbackRecord(**response.data[0])
        raise RuntimeError("Failed to create feedback")
    
    def get_by_job(self, job_id: str):
        """Get feedback for a specific job."""
        from models import FeedbackRecord
        
        if not self.table:
            return None
        
        response = (
            self.table
            .select("*")
            .eq("job_id", job_id)
            .maybe_single()
            .execute()
        )
        
        if response.data:
            return FeedbackRecord(**response.data)
        return None
    
    def get_user_feedback(self, user_id: str, limit: int = 20):
        """Get all feedback from a user."""
        from models import FeedbackRecord
        
        if not self.table:
            return []
        
        response = (
            self.table
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        return [FeedbackRecord(**record) for record in response.data]


class UserPreferenceRepository:
    """Repository for user preferences."""
    
    def __init__(self):
        self.table_name = "user_preferences"
    
    @property
    def client(self):
        return _get_supabase_client()
    
    @property
    def table(self):
        return self.client.table(self.table_name) if self.client else None
    
    def get_or_create(self, user_id: str):
        """Get user preferences, creating default if not exists."""
        from models import UserPreferenceRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        response = (
            self.table
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        
        if response.data:
            return UserPreferenceRecord(**response.data)
        
        # Create default preferences
        preferences = UserPreferenceRecord(user_id=user_id)
        return self.create(preferences)
    
    def create(self, preferences):
        """Create user preferences."""
        from models import UserPreferenceRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        data = preferences.model_dump(mode="json")
        response = self.table.insert(data).execute()
        
        if response.data:
            return UserPreferenceRecord(**response.data[0])
        raise RuntimeError("Failed to create preferences")
    
    def update(self, user_id: str, updates: dict[str, Any]):
        """Update user preferences."""
        from models import UserPreferenceRecord
        
        if not self.table:
            raise RuntimeError("Database not available")
        
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        response = (
            self.table
            .update(updates)
            .eq("user_id", user_id)
            .execute()
        )
        
        if response.data:
            return UserPreferenceRecord(**response.data[0])
        raise RuntimeError(f"Preferences for user {user_id} not found")
