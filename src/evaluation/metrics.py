from collections import defaultdict

from pydantic import BaseModel

from src.evaluation.results import ScenarioResult
from src.evaluation.scenarios import ScenarioCategory
from src.evaluation.verdicts import Verdict


class CategoryMetrics(BaseModel):
    total: int
    pass_rate: float
    partial_rate: float
    fail_rate: float


class Metrics(BaseModel):
    overall: CategoryMetrics
    by_category: dict[ScenarioCategory, CategoryMetrics]


def _rates(results: list[ScenarioResult]) -> CategoryMetrics:
    total = len(results)
    if total == 0:
        return CategoryMetrics(total=0, pass_rate=0.0, partial_rate=0.0, fail_rate=0.0)

    passed = sum(1 for r in results if r.verdict == Verdict.PASS)
    partial = sum(1 for r in results if r.verdict == Verdict.PARTIAL)
    failed = sum(1 for r in results if r.verdict == Verdict.FAIL)

    return CategoryMetrics(
        total=total,
        pass_rate=passed / total,
        partial_rate=partial / total,
        fail_rate=failed / total,
    )


def compute_metrics(results: list[ScenarioResult]) -> Metrics:
    by_category: dict[ScenarioCategory, list[ScenarioResult]] = defaultdict(list)
    for result in results:
        by_category[result.category].append(result)

    return Metrics(
        overall=_rates(results),
        by_category={category: _rates(rs) for category, rs in by_category.items()},
    )
