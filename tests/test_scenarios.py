import json

import pytest
from pydantic import ValidationError

from src.evaluation.scenarios import Scenario, ScenarioCategory, load_scenarios


def test_factual_scenario_requires_expected_substring():
    with pytest.raises(ValidationError):
        Scenario(
            id="s1",
            category=ScenarioCategory.FACTUAL_RECALL,
            turns=["My dog's name is Bruno."],
            final_question="What is my dog's name?",
        )


def test_persona_scenario_requires_persona_expectation():
    with pytest.raises(ValidationError):
        Scenario(
            id="s2",
            category=ScenarioCategory.PERSONA_CONSISTENCY,
            turns=[],
            final_question="Do you like horror movies?",
        )


def test_valid_factual_scenario_constructs():
    scenario = Scenario(
        id="s1",
        category=ScenarioCategory.FACTUAL_RECALL,
        turns=["My dog's name is Bruno."],
        final_question="What is my dog's name?",
        expected_substring="Bruno",
    )
    assert scenario.expected_substring == "Bruno"


def test_valid_persona_scenario_constructs():
    scenario = Scenario(
        id="s2",
        category=ScenarioCategory.PERSONA_CONSISTENCY,
        turns=[],
        final_question="Do you like horror movies?",
        persona_expectation="Should not claim to enjoy horror movies",
    )
    assert scenario.persona_expectation is not None


def test_load_scenarios_reads_jsonl_fixture(tmp_path):
    fixture = tmp_path / "scenarios.jsonl"
    records = [
        {
            "id": "f1",
            "category": "FACTUAL_RECALL",
            "turns": ["My dog's name is Bruno."],
            "final_question": "What is my dog's name?",
            "expected_substring": "Bruno",
        },
        {
            "id": "p1",
            "category": "PERSONA_CONSISTENCY",
            "turns": [],
            "final_question": "Do you like horror movies?",
            "persona_expectation": "Should not claim to enjoy horror movies",
        },
    ]
    fixture.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    scenarios = load_scenarios(fixture)

    assert len(scenarios) == 2
    assert scenarios[0].id == "f1"
    assert scenarios[0].category == ScenarioCategory.FACTUAL_RECALL
    assert scenarios[1].category == ScenarioCategory.PERSONA_CONSISTENCY


def test_load_scenarios_skips_blank_lines(tmp_path):
    fixture = tmp_path / "scenarios.jsonl"
    record = {
        "id": "f1",
        "category": "FACTUAL_RECALL",
        "turns": [],
        "final_question": "q",
        "expected_substring": "x",
    }
    fixture.write_text(f"\n{json.dumps(record)}\n\n", encoding="utf-8")

    scenarios = load_scenarios(fixture)

    assert len(scenarios) == 1
