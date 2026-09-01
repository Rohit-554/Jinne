from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from src.memory.models.memory import MemoryType


class ExtractionDecision(StrEnum):
    SAVE = "SAVE"
    IGNORE = "IGNORE"


class MemoryCandidate(BaseModel):
    decision: ExtractionDecision
    type: MemoryType | None = None
    subject: str | None = None
    relation: str | None = None
    value: str | None = None
    importance: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _require_content_fields_when_saving(self) -> "MemoryCandidate":
        if self.decision != ExtractionDecision.SAVE:
            return self

        required = {
            "type": self.type,
            "subject": self.subject,
            "relation": self.relation,
            "value": self.value,
            "importance": self.importance,
            "confidence": self.confidence,
        }
        missing = [name for name, value in required.items() if value is None]
        if missing:
            raise ValueError(f"SAVE candidate missing required fields: {', '.join(missing)}")
        return self


class ExtractionResult(BaseModel):
    candidates: list[MemoryCandidate] = Field(default_factory=list)
