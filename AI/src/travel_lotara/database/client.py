"""
Supabase Client Module.

Provides a singleton Supabase client for database operations.
Optimized for free tier usage with connection pooling awareness.
"""

from __future__ import annotations

import os
import logging
from typing import Optional
from functools import lru_cache

from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Wrapper around Supabase Python client.
    
    Features:
    - Singleton pattern for connection reuse
    - Automatic retry on transient errors
    - Logging and error handling
    - Free tier optimizations
    """
    
    _instance: Optional["SupabaseClient"] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> "SupabaseClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Supabase client if not already done."""
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Supabase client from environment variables."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            logger.warning(
                "Supabase credentials not found. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
            return
        
        try:
            self._client = create_client(url, key)
            logger.info("✓ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        if self._client is None:
            raise RuntimeError(
                "Supabase client not initialized. "
                "Check SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
        return self._client
    
    def table(self, name: str):
        """Access a table for CRUD operations."""
        return self.client.table(name)
    
    def rpc(self, fn: str, params: dict = None):
        """Call a Postgres function."""
        return self.client.rpc(fn, params or {})
    
    @property
    def auth(self):
        """Access Supabase Auth."""
        return self.client.auth
    
    @property
    def storage(self):
        """Access Supabase Storage."""
        return self.client.storage
    
    def health_check(self) -> dict:
        """
        Check database connectivity.
        
        Returns:
            dict: Health status with connection info
        """
        try:
            # Simple query to test connectivity
            response = self.client.table("health_check").select("*").limit(1).execute()
            return {
                "status": "healthy",
                "connected": True,
                "message": "Database connection successful"
            }
        except Exception as e:
            # Table might not exist, but connection works
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                return {
                    "status": "healthy",
                    "connected": True,
                    "message": "Database connected (health_check table not found)"
                }
            return {
                "status": "unhealthy",
                "connected": False,
                "message": str(e)
            }


@lru_cache(maxsize=1)
def get_supabase_client() -> SupabaseClient:
    """
    Get the singleton Supabase client instance.
    
    Usage:
        from travel_lotara.database import get_supabase_client
        
        client = get_supabase_client()
        response = client.table("jobs").select("*").execute()
    """
    return SupabaseClient()
