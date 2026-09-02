import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.evaluate import evaluate_scenario
from src.evaluation.metrics import compute_metrics
from src.evaluation.results import ScenarioResult
from src.evaluation.runner import EngineFactory
from src.evaluation.scenarios import Scenario
from src.llm.provider import EmbeddingProvider, LLMProvider

METHODOLOGY_NOTE = (
    "Each named system is run against the same scenario dataset using the "
    "same grading logic (deterministic substring checks for factual "
    "categories, an LLM judge for persona consistency). A system's results "
    "may be freshly executed for this comparison, or reused from a prior "
    "canonical evaluation-harness run if that system has not changed since "
    "- either way, every result here reflects a real, previously or newly "
    "executed run, never a fabricated or adjusted number."
)


def run_comparison(
    scenarios: list[Scenario],
    llm: LLMProvider,
    embedder: EmbeddingProvider,
    systems: dict[str, EngineFactory],
) -> dict[str, list[ScenarioResult]]:
    results_by_system: dict[str, list[ScenarioResult]] = {}
    for system_name, engine_factory in systems.items():
        results_by_system[system_name] = [
            evaluate_scenario(scenario, llm, embedder, engine_factory=engine_factory) for scenario in scenarios
        ]
    return results_by_system


def write_comparison_report(
    results_by_system: dict[str, list[ScenarioResult]],
    results_dir: str | Path = "eval/results",
) -> Path:
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = results_dir / f"comparison-{timestamp}.json"

    payload = {
        "methodology": METHODOLOGY_NOTE,
        "systems": {
            system_name: {
                "metrics": json.loads(compute_metrics(results).model_dump_json()),
                "results": [json.loads(result.model_dump_json()) for result in results],
            }
            for system_name, results in results_by_system.items()
        },
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path
