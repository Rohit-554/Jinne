from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel


class ExpectedFact(BaseModel):
    relation: str
    value: str


class ExtractionCase(BaseModel):
    id: str
    message: str
    expected: list[ExpectedFact] = []


def load_extraction_cases(path: str | Path) -> list[ExtractionCase]:
    cases: list[ExtractionCase] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(ExtractionCase.model_validate(json.loads(line)))
    return cases
