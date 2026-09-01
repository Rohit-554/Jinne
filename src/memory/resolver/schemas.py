from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, model_validator


class ResolverAction(StrEnum):
    DUPLICATE = "DUPLICATE"
    SUPERSEDE = "SUPERSEDE"
    INDEPENDENT = "INDEPENDENT"


class ResolverDecision(BaseModel):
    action: ResolverAction
    superseded_memory_id: int | None = None

    @model_validator(mode="after")
    def _require_target_when_matching(self) -> "ResolverDecision":
        if (
            self.action in (ResolverAction.DUPLICATE, ResolverAction.SUPERSEDE)
            and self.superseded_memory_id is None
        ):
            raise ValueError(f"{self.action} decision requires superseded_memory_id")
        return self
