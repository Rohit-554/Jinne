from src.evaluation.extraction_cases import ExpectedFact, ExtractionCase
from src.evaluation.extraction_metrics import (
    CaseScore,
    aggregate_precision_recall,
    score_case,
    values_match,
)
from src.memory.extractor.schemas import ExtractionDecision, MemoryCandidate
from src.memory.models.memory import MemoryType


def _save_candidate(value: str) -> MemoryCandidate:
    return MemoryCandidate(
        decision=ExtractionDecision.SAVE,
        type=MemoryType.OTHER,
        subject="user",
        relation="r",
        value=value,
        importance=0.7,
        confidence=0.9,
    )


def test_values_match_exact():
    assert values_match("Bruno", "Bruno")


def test_values_match_substring_either_direction():
    assert values_match("Microsoft", "Microsoft Corp")
    assert values_match("Microsoft Corp", "Microsoft")


def test_values_match_case_insensitive():
    assert values_match("microsoft", "MICROSOFT")


def test_values_match_non_match():
    assert not values_match("Google", "Microsoft")


def test_score_case_exact_match_has_no_fp_or_fn():
    case = ExtractionCase(id="c1", message="m", expected=[ExpectedFact(relation="works_at", value="Microsoft")])
    score = score_case(case, [_save_candidate("Microsoft")])

    assert score.true_positives == ["Microsoft"]
    assert score.false_positives == []
    assert score.false_negatives == []


def test_score_case_missed_fact_is_false_negative():
    case = ExtractionCase(id="c1", message="m", expected=[ExpectedFact(relation="works_at", value="Microsoft")])
    score = score_case(case, [])

    assert score.false_negatives == ["Microsoft"]
    assert score.true_positives == []


def test_score_case_extra_candidate_is_false_positive():
    case = ExtractionCase(id="c1", message="m", expected=[])
    score = score_case(case, [_save_candidate("Something unexpected")])

    assert score.false_positives == ["Something unexpected"]


def test_score_case_correct_ignore_has_no_fp_or_fn():
    case = ExtractionCase(id="c1", message="hi", expected=[])
    score = score_case(case, [])

    assert score.true_positives == []
    assert score.false_positives == []
    assert score.false_negatives == []


def test_score_case_ignores_non_save_candidates():
    case = ExtractionCase(id="c1", message="m", expected=[])
    ignore_candidate = MemoryCandidate(decision=ExtractionDecision.IGNORE)
    score = score_case(case, [ignore_candidate])

    assert score.false_positives == []


def test_aggregate_precision_recall():
    scores = [
        CaseScore(case_id="a", true_positives=["x", "y"], false_positives=[], false_negatives=[]),
        CaseScore(case_id="b", true_positives=[], false_positives=["z"], false_negatives=["w"]),
    ]

    result = aggregate_precision_recall(scores)

    assert result.true_positive_count == 2
    assert result.false_positive_count == 1
    assert result.false_negative_count == 1
    assert abs(result.precision - (2 / 3)) < 1e-9
    assert abs(result.recall - (2 / 3)) < 1e-9


def test_aggregate_precision_recall_handles_zero_denominator():
    result = aggregate_precision_recall([])

    assert result.precision == 0.0
    assert result.recall == 0.0
