"""
Calendar Tool

Provides calendar gap detection and event creation (HITL-gated).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    title: str
    start: datetime
    end: datetime
    location: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CalendarGap(BaseModel):
    start: datetime
    end: datetime
    hours: float


class CalendarTool:
    """Calendar operations (placeholder for real provider integration)."""

    async def get_gaps(self, start: datetime, end: datetime) -> list[CalendarGap]:
        # Stub: return empty gaps
        return []

    async def propose_event(self, event: CalendarEvent) -> dict[str, Any]:
        """Prepare a calendar event proposal (requires user approval)."""
        return {
            "requires_user_confirmation": True,
            "event": event.model_dump(),
        }
