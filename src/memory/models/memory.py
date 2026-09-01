from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class MemoryType(StrEnum):
    IDENTITY = "IDENTITY"
    RELATIONSHIP = "RELATIONSHIP"
    PREFERENCE = "PREFERENCE"
    CAREER = "CAREER"
    GOAL = "GOAL"
    PLAN = "PLAN"
    EVENT = "EVENT"
    TEMPORARY_STATE = "TEMPORARY_STATE"
    EXPERIENCE = "EXPERIENCE"
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    OTHER = "OTHER"


class MemoryStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"
    UNCERTAIN = "UNCERTAIN"


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Memory(BaseModel):
    id: int | None = None
    type: MemoryType
    subject: str
    relation: str
    value: str
    status: MemoryStatus = MemoryStatus.ACTIVE
    importance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    valid_from: datetime = Field(default_factory=utcnow)
    valid_until: datetime | None = None
    supersedes_memory_id: int | None = None
    source_message_id: str
    embedding: list[float] | None = None
