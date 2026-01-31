"""
State Manager

Tiered memory: Session (short-term) + Persistent (vector DB).
"""

from __future__ import annotations

import threading
from typing import Any

from pydantic import BaseModel, Field


class SessionState(BaseModel):
    session_id: str
    data: dict[str, Any] = Field(default_factory=dict)


class PersistentMemoryItem(BaseModel):
    user_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PersistentMemoryStore:
    """Abstract interface for long-term memory (vector DB)."""

    async def upsert(self, item: PersistentMemoryItem) -> None:
        raise NotImplementedError

    async def query(self, user_id: str, query: str, top_k: int = 5) -> list[PersistentMemoryItem]:
        raise NotImplementedError


class SessionStateManager:
    """Thread-safe session state store."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState:
        with self._lock:
            return self._sessions.setdefault(session_id, SessionState(session_id=session_id))

    def set(self, session_id: str, key: str, value: Any) -> None:
        with self._lock:
            session = self._sessions.setdefault(session_id, SessionState(session_id=session_id))
            session.data[key] = value

    def delete(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
