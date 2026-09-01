from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, model_validator

DETERMINISTIC_CATEGORIES = {
    "FACTUAL_RECALL",
    "LONG_RANGE_RECALL",
    "CONTRADICTION_UPDATE",
    "TEMPORAL_REASONING",
}


class ScenarioCategory(StrEnum):
    FACTUAL_RECALL = "FACTUAL_RECALL"
    LONG_RANGE_RECALL = "LONG_RANGE_RECALL"
    CONTRADICTION_UPDATE = "CONTRADICTION_UPDATE"
    TEMPORAL_REASONING = "TEMPORAL_REASONING"
    PERSONA_CONSISTENCY = "PERSONA_CONSISTENCY"


class Scenario(BaseModel):
    id: str
    category: ScenarioCategory
    turns: list[str]
    final_question: str
    expected_substring: str | None = None
    persona_expectation: str | None = None

    @model_validator(mode="after")
    def _require_expectation_for_category(self) -> "Scenario":
        if self.category == ScenarioCategory.PERSONA_CONSISTENCY:
            if not self.persona_expectation:
                raise ValueError("PERSONA_CONSISTENCY scenarios require persona_expectation")
        elif self.category.value in DETERMINISTIC_CATEGORIES:
            if not self.expected_substring:
                raise ValueError(f"{self.category} scenarios require expected_substring")
        return self


def load_scenarios(path: str | Path) -> list[Scenario]:
    scenarios: list[Scenario] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            scenarios.append(Scenario.model_validate(json.loads(line)))
    return scenarios
