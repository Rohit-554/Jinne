from src.evaluation.baselines import BaselineAEngine, baseline_a_factory
from src.evaluation.runner import run_scenario
from src.evaluation.scenarios import Scenario, ScenarioCategory


class RecordingFakeLLMProvider:
    def __init__(self):
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        return f"reply #{len(self.calls)}"


def test_baseline_a_never_touches_a_memory_store():
    provider = RecordingFakeLLMProvider()
    engine = BaselineAEngine(provider)

    engine.handle_message("My dog's name is Bruno.")
    engine.handle_message("What is my dog's name?")

    # No store attribute at all - BaselineAEngine has no persistence.
    assert not hasattr(engine, "_store")


def test_baseline_a_includes_prior_turns_in_later_messages():
    provider = RecordingFakeLLMProvider()
    engine = BaselineAEngine(provider)

    engine.handle_message("My dog's name is Bruno.")
    engine.handle_message("What is my dog's name?")

    second_call_messages = provider.calls[1]
    contents = [m["content"] for m in second_call_messages]

    assert "My dog's name is Bruno." in contents
    assert "reply #1" in contents
    assert contents[-1] == "What is my dog's name?"


def test_baseline_a_factory_produces_no_persisted_memory_via_run_scenario():
    provider = RecordingFakeLLMProvider()
    scenario = Scenario(
        id="s1",
        category=ScenarioCategory.FACTUAL_RECALL,
        turns=["My dog's name is Bruno."],
        final_question="What is my dog's name?",
        expected_substring="Bruno",
    )

    response, store = run_scenario(scenario, provider, embedder=None, engine_factory=baseline_a_factory)

    try:
        assert response == "reply #2"
        assert store.list() == []
    finally:
        store.close()
