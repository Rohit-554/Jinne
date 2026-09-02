from pydantic import BaseModel

from src.evaluation.extraction_cases import ExtractionCase
from src.memory.extractor.schemas import ExtractionDecision, MemoryCandidate


def values_match(a: str, b: str) -> bool:
    a_lower = a.strip().lower()
    b_lower = b.strip().lower()
    if not a_lower or not b_lower:
        return False
    return a_lower in b_lower or b_lower in a_lower


class CaseScore(BaseModel):
    case_id: str
    true_positives: list[str]
    false_positives: list[str]
    false_negatives: list[str]


def score_case(case: ExtractionCase, actual_candidates: list[MemoryCandidate]) -> CaseScore:
    save_values = [c.value for c in actual_candidates if c.decision == ExtractionDecision.SAVE]

    matched_expected: set[int] = set()
    matched_actual: set[int] = set()

    for expected_index, fact in enumerate(case.expected):
        for actual_index, value in enumerate(save_values):
            if actual_index in matched_actual:
                continue
            if values_match(fact.value, value):
                matched_expected.add(expected_index)
                matched_actual.add(actual_index)
                break

    true_positives = [case.expected[i].value for i in matched_expected]
    false_negatives = [fact.value for i, fact in enumerate(case.expected) if i not in matched_expected]
    false_positives = [value for i, value in enumerate(save_values) if i not in matched_actual]

    return CaseScore(
        case_id=case.id,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


class PrecisionRecall(BaseModel):
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    precision: float
    recall: float


def aggregate_precision_recall(case_scores: list[CaseScore]) -> PrecisionRecall:
    tp = sum(len(s.true_positives) for s in case_scores)
    fp = sum(len(s.false_positives) for s in case_scores)
    fn = sum(len(s.false_negatives) for s in case_scores)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return PrecisionRecall(
        true_positive_count=tp,
        false_positive_count=fp,
        false_negative_count=fn,
        precision=precision,
        recall=recall,
    )
