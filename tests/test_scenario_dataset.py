from collections import Counter
from pathlib import Path

from src.evaluation.scenarios import ScenarioCategory, load_scenarios

SCENARIOS_PATH = Path(__file__).resolve().parent.parent / "eval" / "scenarios" / "scenarios.jsonl"


def test_dataset_parses_and_has_at_least_ten_per_category():
    scenarios = load_scenarios(SCENARIOS_PATH)

    assert len(scenarios) >= 50

    counts = Counter(s.category for s in scenarios)
    for category in ScenarioCategory:
        assert counts[category] >= 10, f"{category} has only {counts[category]} scenarios"


def test_dataset_ids_are_unique():
    scenarios = load_scenarios(SCENARIOS_PATH)
    ids = [s.id for s in scenarios]
    assert len(ids) == len(set(ids))


def test_long_range_scenarios_have_intervening_turns():
    scenarios = load_scenarios(SCENARIOS_PATH)
    long_range = [s for s in scenarios if s.category == ScenarioCategory.LONG_RANGE_RECALL]

    assert len(long_range) >= 10
    for scenario in long_range:
        # fact-establishing turn + several filler turns before the final question
        assert len(scenario.turns) >= 4
