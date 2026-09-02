from pathlib import Path

from src.evaluation.extraction_cases import load_extraction_cases

CASES_PATH = Path(__file__).resolve().parent.parent / "eval" / "scenarios" / "extraction_cases.jsonl"


def test_dataset_parses_and_has_at_least_twenty_cases():
    cases = load_extraction_cases(CASES_PATH)
    assert len(cases) >= 20


def test_dataset_has_both_save_and_ignore_cases():
    cases = load_extraction_cases(CASES_PATH)
    save_cases = [c for c in cases if c.expected]
    ignore_cases = [c for c in cases if not c.expected]

    assert len(save_cases) >= 5
    assert len(ignore_cases) >= 5


def test_dataset_ids_are_unique():
    cases = load_extraction_cases(CASES_PATH)
    ids = [c.id for c in cases]
    assert len(ids) == len(set(ids))
