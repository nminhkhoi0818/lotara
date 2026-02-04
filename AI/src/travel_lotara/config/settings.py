"""Configuration settings for Travel Lotara."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field
from google.genai import types  # Import for generation configs

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are set systemically


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    
    # Opik Configuration
    opik_api_key: str | None = Field(default=None)
    opik_project_name: str = Field(default="lotara-travel")
    opik_workspace_name: str = Field(default="lotara-workspace")
    opik_tags: list[str] = Field(default_factory=lambda: ["travel", "multi-agent", "adk"])
    project_environment: str = Field(default="development")
    
    # Google AI Configuration
    google_api_key: str | None = Field(default=None)
    gemini_api_key: str | None = Field(default=None)  # Alias for google_api_key
    
    # Model Configuration - Use direct model name for ADK, not LiteLLM format
    model: str = Field(default="gemini-2.5-flash")
    
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
    version: str = Field(default="0.1.0")
    
    @property
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.supabase_url and (self.supabase_anon_key or self.supabase_service_role_key))


def load_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings(
        # Opik
        opik_api_key=os.getenv("OPIK_API_KEY"),
        opik_project_name=os.getenv("OPIK_PROJECT_NAME", "lotara-travel"),
        opik_workspace_name=os.getenv("OPIK_WORKSPACE_NAME", "lotara-workspace"),
        project_environment=os.getenv("ENV", os.getenv("ENVIRONMENT", "development")),
        
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
        version=os.getenv("VERSION", "0.1.0")
    )


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern for performance)."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings

def reload_settings() -> Settings:
    """Force reload settings from environment (use only when needed)."""
    global _settings
    _settings = None
    return get_settings()


# -----------------------------------------------------------------------------
# OPTIMIZED GENERATION CONFIGS FOR PERFORMANCE
# -----------------------------------------------------------------------------

# Fast generation config for intermediate agents (inspiration, planning)
# Higher temperature and limits for faster generation
FAST_GENERATION_CONFIG = types.GenerateContentConfig(
    temperature=1.0,              # Higher temp = faster, more creative
    top_p=0.95,                   # Nucleus sampling for speed
    top_k=40,                     # Limit candidates for speed
    candidate_count=1,            # Only generate 1 response
    max_output_tokens=8000,       # Prevent runaway generation
    stop_sequences=[],            # No custom stop sequences
    response_modalities=["TEXT"], # Explicit text-only
)

# JSON generation config for agents WITHOUT tools (e.g., pure formatter)
# Lower temperature for structured, consistent output
JSON_GENERATION_CONFIG = types.GenerateContentConfig(
    temperature=0.3,              # Lower temp for structured output
    top_p=0.8,                    # More focused sampling
    top_k=20,                     # Limit options for consistency
    candidate_count=1,            # Single response
    max_output_tokens=16000,      # Large enough for full itinerary JSON
    response_mime_type="application/json",  # Force JSON format (incompatible with tools)
)

# JSON generation config for agents WITH tools
# Cannot use response_mime_type='application/json' with function calling
# Relies on output_schema instead for JSON formatting
TOOL_COMPATIBLE_JSON_CONFIG = types.GenerateContentConfig(
    temperature=0.3,              # Lower temp for structured output
    top_p=0.8,                    # More focused sampling
    top_k=20,                     # Limit options for consistency
    candidate_count=1,            # Single response
    max_output_tokens=16000,      # Large enough for full itinerary JSON
    # NO response_mime_type - let output_schema handle JSON formatting
)

# Optimized retry config - faster retries for production
# Reduced delays for better UX while still handling transient errors
# Note: HttpRetryOptions only accepts initial_delay and max_delay
FAST_HTTP_RETRY_OPTIONS = types.HttpRetryOptions(
    initial_delay=10.0,          # 10s instead of 60s
    max_delay=30.0,              # Cap at 30s instead of unlimited
)

FAST_HTTP_OPTIONS = types.HttpOptions(
    retry_options=FAST_HTTP_RETRY_OPTIONS
)
