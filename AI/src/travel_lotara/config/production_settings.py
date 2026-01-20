"""
Production Configuration Settings

Extended settings for multi-user production deployment.
"""

from __future__ import annotations

import os
from typing import Optional
from pydantic import BaseModel, Field, validator


class DatabaseSettings(BaseModel):
    """PostgreSQL database configuration."""
    url: str = Field(default="postgresql+asyncpg://user:pass@localhost:5432/travel_lotara")
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=40)
    echo: bool = Field(default=False)


class RateLimitSettings(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = Field(default=True)
    requests_per_minute_per_ip: int = Field(default=10)
    requests_per_day_per_user: int = Field(default=100)


class ResourceSettings(BaseModel):
    """Resource management configuration."""
    max_concurrent_requests: int = Field(default=100)
    max_concurrent_per_user: int = Field(default=3)
    request_timeout_seconds: int = Field(default=600)  # 10 minutes
    queue_size: int = Field(default=1000)


class SecuritySettings(BaseModel):
    """Security configuration."""
    jwt_secret_key: str = Field(...)
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    max_query_length: int = Field(default=5000)
    
    @validator("jwt_secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")
        return v


class CostSettings(BaseModel):
    """Cost management configuration."""
    default_monthly_budget_usd: float = Field(default=100.0)
    free_tier_daily_requests: int = Field(default=10)
    pro_tier_daily_requests: int = Field(default=100)
    enterprise_tier_daily_requests: int = Field(default=1000)


class ProductionSettings(BaseModel):
    """Complete production configuration."""
    
    # Environment
    environment: str = Field(default="development")  # development, staging, production
    debug: bool = Field(default=False)
    
    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_workers: int = Field(default=4)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    
    # Services (Simplified for MVP - PostgreSQL only)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    resources: ResourceSettings = Field(default_factory=ResourceSettings)
    security: SecuritySettings
    cost: CostSettings = Field(default_factory=CostSettings)
    
    # External APIs
    opik_api_key: Optional[str] = Field(default=None)
    opik_project: str = Field(default="travel-lotara-prod")
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    
    # Logging
    log_level: str = Field(default="INFO")
    sentry_dsn: Optional[str] = Field(default=None)
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v


def load_production_settings() -> ProductionSettings:
    """
    Load production settings from environment variables.
    
    Required env vars:
    - JWT_SECRET_KEY
    
    Optional env vars:
    - ENVIRONMENT (default: development)
    - DATABASE_URL
    - OPIK_API_KEY
    - OPENAI_API_KEY
    - GOOGLE_API_KEY
    """
    return ProductionSettings(
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        
        # API
        api_host=os.getenv("API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("API_PORT", "8000")),
        api_workers=int(os.getenv("API_WORKERS", "4")),
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        
        # Database
        database=DatabaseSettings(
            url=os.getenv(
                "DATABASE_URL",
                "postgresql+asyncpg://user:pass@localhost:5432/travel_lotara"
            ),
        ),
        
        # Security (REQUIRED)
        security=SecuritySettings(
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", ""),
            access_token_expire_minutes=int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
            ),
        ),
        
        # External APIs
        opik_api_key=os.getenv("OPIK_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        
        # Logging
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        sentry_dsn=os.getenv("SENTRY_DSN"),
    )


# Example usage
if __name__ == "__main__":
    settings = load_production_settings()
    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database.url}")
    print(f"Max concurrent requests: {settings.resources.max_concurrent_requests}")
