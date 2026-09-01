import pytest
from pydantic import ValidationError

from src.memory.extractor.schemas import ExtractionDecision, ExtractionResult, MemoryCandidate
from src.memory.models.memory import MemoryType


def test_save_candidate_with_all_fields_is_valid():
    candidate = MemoryCandidate(
        decision=ExtractionDecision.SAVE,
        type=MemoryType.CAREER,
        subject="user",
        relation="works_at",
        value="Microsoft",
        importance=0.9,
        confidence=0.95,
    )
    assert candidate.decision == ExtractionDecision.SAVE


def test_ignore_candidate_needs_no_content_fields():
    candidate = MemoryCandidate(decision=ExtractionDecision.IGNORE)
    assert candidate.value is None


def test_save_candidate_missing_value_is_invalid():
    with pytest.raises(ValidationError):
        MemoryCandidate(
            decision=ExtractionDecision.SAVE,
            type=MemoryType.CAREER,
            subject="user",
            relation="works_at",
            # value is missing
            importance=0.9,
            confidence=0.95,
        )


def test_save_candidate_with_out_of_range_importance_is_invalid():
    with pytest.raises(ValidationError):
        MemoryCandidate(
            decision=ExtractionDecision.SAVE,
            type=MemoryType.CAREER,
            subject="user",
            relation="works_at",
            value="Microsoft",
            importance=1.5,
            confidence=0.95,
        )


def test_extraction_result_parses_from_llm_style_json():
    result = ExtractionResult.model_validate(
        {
            "candidates": [
                {
                    "decision": "SAVE",
                    "type": "CAREER",
                    "subject": "user",
                    "relation": "works_at",
                    "value": "Microsoft",
                    "importance": 0.9,
                    "confidence": 0.95,
                }
            ]
        }
    )
    assert len(result.candidates) == 1
    assert result.candidates[0].value == "Microsoft"


def test_extraction_result_rejects_invalid_decision_value():
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate({"candidates": [{"decision": "MAYBE"}]})
