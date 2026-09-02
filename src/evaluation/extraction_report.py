import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.extraction_cases import ExtractionCase
from src.evaluation.extraction_metrics import CaseScore, aggregate_precision_recall, score_case
from src.llm.provider import LLMProvider
from src.memory.extractor.extractor import MemoryExtractor

METHODOLOGY_NOTE = (
    "Each case's message is run through the real MemoryExtractor (a live "
    "LLM call, no mocks). Actual SAVE candidates are matched against the "
    "case's expected facts by value only (case-insensitive substring match "
    "in either direction), not by exact relation string, since reasonable "
    "relation-naming choices can vary between extraction calls without the "
    "extracted fact being wrong. Precision = TP / (TP + FP), "
    "recall = TP / (TP + FN), computed only from cases that were actually run."
)


def run_extraction_metrics(cases: list[ExtractionCase], llm: LLMProvider) -> list[CaseScore]:
    extractor = MemoryExtractor(llm)
    scores = []
    for case in cases:
        candidates = extractor.extract(case.message)
        scores.append(score_case(case, candidates))
    return scores


def write_extraction_report(case_scores: list[CaseScore], results_dir: str | Path = "eval/results") -> Path:
    precision_recall = aggregate_precision_recall(case_scores)
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = results_dir / f"extraction-metrics-{timestamp}.json"

    payload = {
        "methodology": METHODOLOGY_NOTE,
        "precision_recall": json.loads(precision_recall.model_dump_json()),
        "case_scores": [json.loads(score.model_dump_json()) for score in case_scores],
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path
