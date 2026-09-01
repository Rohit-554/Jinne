from src.evaluation.metrics import compute_metrics
from src.evaluation.results import ScenarioResult
from src.evaluation.scenarios import ScenarioCategory
from src.evaluation.verdicts import Verdict


def _result(category, verdict, id_suffix="") -> ScenarioResult:
    return ScenarioResult(
        scenario_id=f"{category}-{verdict}{id_suffix}",
        category=category,
        verdict=verdict,
        response="some response",
        expected="some expectation",
    )


def test_overall_rates_computed_from_all_results():
    results = [
        _result(ScenarioCategory.FACTUAL_RECALL, Verdict.PASS),
        _result(ScenarioCategory.FACTUAL_RECALL, Verdict.PASS, "-2"),
        _result(ScenarioCategory.FACTUAL_RECALL, Verdict.FAIL),
        _result(ScenarioCategory.PERSONA_CONSISTENCY, Verdict.PARTIAL),
    ]

    metrics = compute_metrics(results)

    assert metrics.overall.total == 4
    assert metrics.overall.pass_rate == 0.5
    assert metrics.overall.fail_rate == 0.25
    assert metrics.overall.partial_rate == 0.25


def test_per_category_rates_are_independent():
    results = [
        _result(ScenarioCategory.FACTUAL_RECALL, Verdict.PASS),
        _result(ScenarioCategory.FACTUAL_RECALL, Verdict.PASS, "-2"),
        _result(ScenarioCategory.PERSONA_CONSISTENCY, Verdict.FAIL),
    ]

    metrics = compute_metrics(results)

    assert metrics.by_category[ScenarioCategory.FACTUAL_RECALL].pass_rate == 1.0
    assert metrics.by_category[ScenarioCategory.PERSONA_CONSISTENCY].pass_rate == 0.0
    assert metrics.by_category[ScenarioCategory.PERSONA_CONSISTENCY].fail_rate == 1.0


def test_empty_results_produce_zeroed_metrics():
    metrics = compute_metrics([])

    assert metrics.overall.total == 0
    assert metrics.overall.pass_rate == 0.0
