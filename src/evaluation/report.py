import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.metrics import compute_metrics
from src.evaluation.results import ScenarioResult

METHODOLOGY_NOTE = (
    "Factual recall, long-range recall, contradiction/update, and temporal "
    "reasoning verdicts are deterministic substring checks against the "
    "actual response. Persona consistency verdicts come from an LLM judge "
    "and carry its known limitations: potential judge bias, "
    "nondeterminism, and correlation between the model generating the "
    "responses and the model judging them."
)


def write_report(results: list[ScenarioResult], results_dir: str | Path = "eval/results") -> Path:
    metrics = compute_metrics(results)
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = results_dir / f"run-{timestamp}.json"

    payload = {
        "methodology": METHODOLOGY_NOTE,
        "metrics": json.loads(metrics.model_dump_json()),
        "results": [json.loads(result.model_dump_json()) for result in results],
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path
