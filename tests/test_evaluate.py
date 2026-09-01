from src.evaluation.evaluate import evaluate_scenario
from src.evaluation.scenarios import Scenario, ScenarioCategory
from src.evaluation.verdicts import Verdict

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"
JUDGE_SYSTEM_PREFIX = "You are an evaluation judge"


class RoutingFakeLLMProvider:
    def __init__(self, chat_reply: str, judge_response: str | None = None):
        self._chat_reply = chat_reply
        self._judge_response = judge_response

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            return '{"candidates": []}'
        if system_content.startswith(JUDGE_SYSTEM_PREFIX):
            return self._judge_response
        return self._chat_reply


class FakeEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [1.0, 0.0]


def test_deterministic_category_uses_substring_check_not_judge():
    scenario = Scenario(
        id="fact-01",
        category=ScenarioCategory.FACTUAL_RECALL,
        turns=["My dog's name is Bruno."],
        final_question="What's my dog's name?",
        expected_substring="Bruno",
    )
    provider = RoutingFakeLLMProvider(chat_reply="Your dog's name is Bruno!", judge_response="SHOULD NOT BE CALLED")

    result = evaluate_scenario(scenario, provider, FakeEmbeddingProvider())

    assert result.scenario_id == "fact-01"
    assert result.category == ScenarioCategory.FACTUAL_RECALL
    assert result.verdict == Verdict.PASS
    assert result.response == "Your dog's name is Bruno!"
    assert result.expected == "Bruno"
    assert result.reasoning is None


def test_deterministic_category_fails_when_expected_fact_missing():
    scenario = Scenario(
        id="fact-02",
        category=ScenarioCategory.FACTUAL_RECALL,
        turns=["My dog's name is Bruno."],
        final_question="What's my dog's name?",
        expected_substring="Bruno",
    )
    provider = RoutingFakeLLMProvider(chat_reply="I'm not sure, remind me?")

    result = evaluate_scenario(scenario, provider, FakeEmbeddingProvider())

    assert result.verdict == Verdict.FAIL


def test_persona_category_uses_judge():
    scenario = Scenario(
        id="persona-01",
        category=ScenarioCategory.PERSONA_CONSISTENCY,
        turns=[],
        final_question="Do you like horror movies?",
        persona_expectation="Should express dislike of horror movies",
    )
    provider = RoutingFakeLLMProvider(
        chat_reply="Nope, horror's not my thing - too much screaming, not enough plot twists I like.",
        judge_response='{"verdict": "PASS", "reasoning": "Expressed dislike of horror in character."}',
    )

    result = evaluate_scenario(scenario, provider, FakeEmbeddingProvider())

    assert result.scenario_id == "persona-01"
    assert result.category == ScenarioCategory.PERSONA_CONSISTENCY
    assert result.verdict == Verdict.PASS
    assert result.expected == "Should express dislike of horror movies"
    assert result.reasoning == "Expressed dislike of horror in character."
