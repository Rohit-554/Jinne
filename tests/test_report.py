import json

from src.evaluation.report import write_report
from src.evaluation.results import ScenarioResult
from src.evaluation.scenarios import ScenarioCategory
from src.evaluation.verdicts import Verdict


def _results() -> list[ScenarioResult]:
    return [
        ScenarioResult(
            scenario_id="fact-01",
            category=ScenarioCategory.FACTUAL_RECALL,
            verdict=Verdict.PASS,
            response="Your dog's name is Bruno!",
            expected="Bruno",
        ),
        ScenarioResult(
            scenario_id="contra-01",
            category=ScenarioCategory.CONTRADICTION_UPDATE,
            verdict=Verdict.FAIL,
            response="I think you work at Google.",
            expected="Microsoft",
        ),
        ScenarioResult(
            scenario_id="persona-01",
            category=ScenarioCategory.PERSONA_CONSISTENCY,
            verdict=Verdict.PARTIAL,
            response="I guess horror movies are okay sometimes.",
            expected="Should express dislike of horror movies",
            reasoning="Mixed signal on horror movie preference.",
        ),
    ]


def test_write_report_round_trips_metrics_and_results(tmp_path):
    results = _results()

    report_path = write_report(results, results_dir=tmp_path)

    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["metrics"]["overall"]["total"] == 3
    assert len(payload["results"]) == 3
    assert {r["scenario_id"] for r in payload["results"]} == {"fact-01", "contra-01", "persona-01"}


def test_write_report_includes_failure_detail_for_non_pass_scenarios(tmp_path):
    results = _results()

    report_path = write_report(results, results_dir=tmp_path)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    by_id = {r["scenario_id"]: r for r in payload["results"]}

    failed = by_id["contra-01"]
    assert failed["verdict"] == "FAIL"
    assert failed["expected"] == "Microsoft"
    assert failed["response"] == "I think you work at Google."

    partial = by_id["persona-01"]
    assert partial["verdict"] == "PARTIAL"
    assert partial["reasoning"] == "Mixed signal on horror movie preference."


def test_write_report_creates_results_dir_if_missing(tmp_path):
    nested_dir = tmp_path / "nested" / "results"

    report_path = write_report(_results(), results_dir=nested_dir)

    assert report_path.exists()
    assert report_path.parent == nested_dir
