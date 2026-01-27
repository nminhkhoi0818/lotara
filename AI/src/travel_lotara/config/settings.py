"""Configuration settings for Travel Lotara."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    
    # Opik Configuration
    opik_api_key: str | None = Field(default=None)
    opik_project: str = Field(default="lotara-travel")
    opik_tags: list[str] = Field(default_factory=lambda: ["travel", "multi-agent", "adk"])
    
    # Google AI Configuration
    google_api_key: str | None = Field(default=None)
    gemini_api_key: str | None = Field(default=None)  # Alias for google_api_key
    
    # Model Configuration (LiteLLM format)
    model: str = Field(default="gemini/gemini-2.5-flash")
    
    # Budget Defaults
    default_budget_usd: float = Field(default=1000.0, ge=0.0)
    default_budget_tokens: int = Field(default=100000, ge=0)
    
    # Supabase Configuration
    supabase_url: str | None = Field(default=None)
    supabase_anon_key: str | None = Field(default=None)
    supabase_service_role_key: str | None = Field(default=None)
    
    # Legacy Database URL (for direct PostgreSQL connections)
    database_url: str | None = Field(default=None)
    
    # Environment
    environment: str = Field(default="development")
    
    @property
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.supabase_url and (self.supabase_anon_key or self.supabase_service_role_key))


def load_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings(
        # Opik
        opik_api_key=os.getenv("OPIK_API_KEY"),
        opik_project=os.getenv("OPIK_PROJECT_NAME", "lotara-travel"),
        
        # Google AI
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        
        # Model (LiteLLM format)
        model=os.getenv("LOTARA_MODEL", "gemini-2.5-flash"),

        # Budgets
        default_budget_usd=float(os.getenv("DEFAULT_BUDGET_USD", "1000")),
        default_budget_tokens=int(os.getenv("DEFAULT_BUDGET_TOKENS", "100000")),
        
        # Supabase
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        
        # Legacy Database
        database_url=os.getenv("DATABASE_URL"),
        
        # Environment
        environment=os.getenv("ENVIRONMENT", "development"),
    )


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings

