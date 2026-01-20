"""
Repository Classes for Database Operations.

Provides high-level CRUD operations for each entity type.
Follows repository pattern for clean separation of concerns.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional, TypeVar, Generic

from travel_lotara.database.client import get_supabase_client, SupabaseClient
from travel_lotara.database.models import (
    JobRecord,
    SessionRecord,
    FeedbackRecord,
    UserPreferenceRecord,
    TravelItineraryRecord,
    JobStatus,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._client: Optional[SupabaseClient] = None
    
    @property
    def client(self) -> SupabaseClient:
        """Lazy-load Supabase client."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client
    
    @property
    def table(self):
        """Get the table reference."""
        return self.client.table(self.table_name)


class JobRepository(BaseRepository[JobRecord]):
    """
    Repository for job records.
    
    Handles CRUD operations for workflow jobs.
    """
    
    def __init__(self):
        super().__init__("jobs")
    
    def create(self, job: JobRecord) -> JobRecord:
        """
        Create a new job record.
        
        Args:
            job: Job record to create
            
        Returns:
            Created job record with database-generated fields
        """
        try:
            data = job.model_dump(mode="json")
            response = self.table.insert(data).execute()
            
            if response.data:
                logger.info(f"Created job: {job.id}")
                return JobRecord(**response.data[0])
            raise RuntimeError("Failed to create job record")
            
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            raise
    
    def get_by_id(self, job_id: str) -> Optional[JobRecord]:
        """
        Get a job by ID.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Job record or None if not found
        """
        try:
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
            
        except Exception as e:
            logger.error(f"Error fetching job {job_id}: {e}")
            raise
    
    def get_by_user(
        self, 
        user_id: str, 
        limit: int = 10,
        status: Optional[JobStatus] = None
    ) -> list[JobRecord]:
        """
        Get jobs for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of records
            status: Optional status filter
            
        Returns:
            List of job records
        """
        try:
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
            
        except Exception as e:
            logger.error(f"Error fetching jobs for user {user_id}: {e}")
            raise
    
    def update(self, job_id: str, updates: dict[str, Any]) -> JobRecord:
        """
        Update a job record.
        
        Args:
            job_id: Job identifier
            updates: Fields to update
            
        Returns:
            Updated job record
        """
        try:
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
            
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            raise
    
    def update_status(
        self, 
        job_id: str, 
        status: JobStatus,
        partial_outputs: Optional[dict] = None,
        error: Optional[dict] = None
    ) -> JobRecord:
        """
        Update job status with optional outputs.
        
        Args:
            job_id: Job identifier
            status: New status
            partial_outputs: Partial results
            error: Error details if failed
            
        Returns:
            Updated job record
        """
        updates = {"status": status.value}
        
        if partial_outputs:
            updates["partial_outputs"] = partial_outputs
        
        if error:
            updates["error"] = error
        
        if status == JobStatus.COMPLETED:
            updates["completed_at"] = datetime.utcnow().isoformat()
        
        return self.update(job_id, updates)
    
    def delete(self, job_id: str) -> bool:
        """
        Delete a job record.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            response = (
                self.table
                .delete()
                .eq("id", job_id)
                .execute()
            )
            logger.info(f"Deleted job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            raise


class SessionRepository(BaseRepository[SessionRecord]):
    """
    Repository for session records.
    
    Handles conversation context persistence.
    """
    
    def __init__(self):
        super().__init__("sessions")
    
    def create(self, session: SessionRecord) -> SessionRecord:
        """Create a new session."""
        try:
            data = session.model_dump(mode="json")
            response = self.table.insert(data).execute()
            
            if response.data:
                logger.info(f"Created session: {session.id}")
                return SessionRecord(**response.data[0])
            raise RuntimeError("Failed to create session")
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def get_by_id(self, session_id: str) -> Optional[SessionRecord]:
        """Get session by ID."""
        try:
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
            
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {e}")
            raise
    
    def get_active_session(self, user_id: str) -> Optional[SessionRecord]:
        """Get the user's current active session."""
        try:
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
            
        except Exception as e:
            logger.error(f"Error fetching active session for user {user_id}: {e}")
            raise
    
    def update(self, session_id: str, updates: dict[str, Any]) -> SessionRecord:
        """Update a session."""
        try:
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
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            raise
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[dict] = None
    ) -> SessionRecord:
        """
        Add a message to session history.
        
        Keeps only recent messages to optimize for free tier storage.
        """
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
    
    def deactivate(self, session_id: str) -> SessionRecord:
        """Deactivate a session."""
        return self.update(session_id, {"is_active": False})


class FeedbackRepository(BaseRepository[FeedbackRecord]):
    """
    Repository for feedback records.
    
    Stores user ratings and comments for evaluation.
    """
    
    def __init__(self):
        super().__init__("feedback")
    
    def create(self, feedback: FeedbackRecord) -> FeedbackRecord:
        """Create a feedback record."""
        try:
            data = feedback.model_dump(mode="json")
            response = self.table.insert(data).execute()
            
            if response.data:
                logger.info(f"Created feedback: {feedback.id}")
                return FeedbackRecord(**response.data[0])
            raise RuntimeError("Failed to create feedback")
            
        except Exception as e:
            logger.error(f"Error creating feedback: {e}")
            raise
    
    def get_by_job(self, job_id: str) -> Optional[FeedbackRecord]:
        """Get feedback for a specific job."""
        try:
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
            
        except Exception as e:
            logger.error(f"Error fetching feedback for job {job_id}: {e}")
            raise
    
    def get_user_feedback(self, user_id: str, limit: int = 20) -> list[FeedbackRecord]:
        """Get all feedback from a user."""
        try:
            response = (
                self.table
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return [FeedbackRecord(**record) for record in response.data]
            
        except Exception as e:
            logger.error(f"Error fetching feedback for user {user_id}: {e}")
            raise
    
    def get_average_rating(self, user_id: Optional[str] = None) -> float:
        """Get average rating, optionally filtered by user."""
        try:
            query = self.table.select("rating")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            response = query.execute()
            
            if response.data:
                ratings = [r["rating"] for r in response.data]
                return sum(ratings) / len(ratings)
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average rating: {e}")
            return 0.0


class UserPreferenceRepository(BaseRepository[UserPreferenceRecord]):
    """
    Repository for user preferences.
    
    Stores and retrieves personalization data.
    """
    
    def __init__(self):
        super().__init__("user_preferences")
    
    def get_or_create(self, user_id: str) -> UserPreferenceRecord:
        """Get user preferences, creating default if not exists."""
        try:
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
            
        except Exception as e:
            logger.error(f"Error fetching preferences for user {user_id}: {e}")
            raise
    
    def create(self, preferences: UserPreferenceRecord) -> UserPreferenceRecord:
        """Create user preferences."""
        try:
            data = preferences.model_dump(mode="json")
            response = self.table.insert(data).execute()
            
            if response.data:
                logger.info(f"Created preferences for user: {preferences.user_id}")
                return UserPreferenceRecord(**response.data[0])
            raise RuntimeError("Failed to create preferences")
            
        except Exception as e:
            logger.error(f"Error creating preferences: {e}")
            raise
    
    def update(self, user_id: str, updates: dict[str, Any]) -> UserPreferenceRecord:
        """Update user preferences."""
        try:
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
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            raise
    
    def add_destination_to_history(self, user_id: str, destination: str) -> None:
        """Add a visited destination to user history."""
        preferences = self.get_or_create(user_id)
        
        past_destinations = preferences.past_destinations
        if destination not in past_destinations:
            past_destinations.append(destination)
            # Keep only last 50 destinations
            past_destinations = past_destinations[-50:]
            
        self.update(user_id, {"past_destinations": past_destinations})


class ItineraryRepository(BaseRepository[TravelItineraryRecord]):
    """
    Repository for saved itineraries.
    
    Stores finalized travel plans.
    """
    
    def __init__(self):
        super().__init__("itineraries")
    
    def create(self, itinerary: TravelItineraryRecord) -> TravelItineraryRecord:
        """Create a saved itinerary."""
        try:
            data = itinerary.model_dump(mode="json")
            response = self.table.insert(data).execute()
            
            if response.data:
                logger.info(f"Created itinerary: {itinerary.id}")
                return TravelItineraryRecord(**response.data[0])
            raise RuntimeError("Failed to create itinerary")
            
        except Exception as e:
            logger.error(f"Error creating itinerary: {e}")
            raise
    
    def get_by_user(
        self, 
        user_id: str, 
        limit: int = 10,
        include_booked: bool = True
    ) -> list[TravelItineraryRecord]:
        """Get itineraries for a user."""
        try:
            query = (
                self.table
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
            )
            
            if not include_booked:
                query = query.eq("is_booked", False)
            
            response = query.execute()
            return [TravelItineraryRecord(**record) for record in response.data]
            
        except Exception as e:
            logger.error(f"Error fetching itineraries for user {user_id}: {e}")
            raise
    
    def get_by_id(self, itinerary_id: str) -> Optional[TravelItineraryRecord]:
        """Get itinerary by ID."""
        try:
            response = (
                self.table
                .select("*")
                .eq("id", itinerary_id)
                .maybe_single()
                .execute()
            )
            
            if response.data:
                return TravelItineraryRecord(**response.data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching itinerary {itinerary_id}: {e}")
            raise
    
    def mark_as_booked(
        self, 
        itinerary_id: str, 
        booking_references: list[dict]
    ) -> TravelItineraryRecord:
        """Mark itinerary as booked with references."""
        try:
            updates = {
                "is_booked": True,
                "booking_references": booking_references,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = (
                self.table
                .update(updates)
                .eq("id", itinerary_id)
                .execute()
            )
            
            if response.data:
                return TravelItineraryRecord(**response.data[0])
            raise RuntimeError(f"Itinerary {itinerary_id} not found")
            
        except Exception as e:
            logger.error(f"Error marking itinerary as booked: {e}")
            raise
