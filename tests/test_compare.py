import json

from src.evaluation.compare import run_comparison, write_comparison_report
from src.evaluation.scenarios import Scenario, ScenarioCategory

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"


class FakeLLMProvider:
    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            return '{"candidates": []}'
        return "a reply containing Bruno"


class FakeEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [1.0, 0.0]


class FakeSystemA:
    def __init__(self, llm, embedder, store):
        self._llm = llm

    def handle_message(self, user_message: str) -> str:
        return self._llm.complete([{"role": "system", "content": "chat"}, {"role": "user", "content": user_message}])


class FakeSystemB:
    def __init__(self, llm, embedder, store):
        self._llm = llm

    def handle_message(self, user_message: str) -> str:
        return "a reply without the fact"


def _scenarios() -> list[Scenario]:
    return [
        Scenario(
            id="fact-01",
            category=ScenarioCategory.FACTUAL_RECALL,
            turns=["My dog's name is Bruno."],
            final_question="What is my dog's name?",
            expected_substring="Bruno",
        ),
        Scenario(
            id="fact-02",
            category=ScenarioCategory.FACTUAL_RECALL,
            turns=["My cat's name is Luna."],
            final_question="What is my cat's name?",
            expected_substring="Luna",
        ),
    ]


def test_run_comparison_runs_every_scenario_against_every_system():
    results = run_comparison(
        _scenarios(),
        FakeLLMProvider(),
        FakeEmbeddingProvider(),
        systems={"system_a": FakeSystemA, "system_b": FakeSystemB},
    )

    assert set(results.keys()) == {"system_a", "system_b"}
    assert len(results["system_a"]) == 2
    assert len(results["system_b"]) == 2


def test_write_comparison_report_includes_all_systems(tmp_path):
    results = run_comparison(
        _scenarios(),
        FakeLLMProvider(),
        FakeEmbeddingProvider(),
        systems={"system_a": FakeSystemA, "system_b": FakeSystemB},
    )

    report_path = write_comparison_report(results, results_dir=tmp_path)

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert set(payload["systems"].keys()) == {"system_a", "system_b"}
    assert payload["systems"]["system_a"]["metrics"]["overall"]["total"] == 2
    assert payload["systems"]["system_b"]["metrics"]["overall"]["total"] == 2
    assert len(payload["systems"]["system_a"]["results"]) == 2
