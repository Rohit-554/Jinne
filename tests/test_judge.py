from src.evaluation.judge import judge_persona_consistency
from src.evaluation.verdicts import Verdict
from src.persona.persona import DEFAULT_PERSONA


class FakeLLMProvider:
    def __init__(self, response: str):
        self._response = response

    def complete(self, messages: list[dict[str, str]]) -> str:
        return self._response


def test_judge_parses_pass_verdict():
    provider = FakeLLMProvider('{"verdict": "PASS", "reasoning": "Stayed casual and in character."}')

    judgment = judge_persona_consistency(
        provider, DEFAULT_PERSONA, "Should not use generic AI disclaimers", "Hey, happy to help!"
    )

    assert judgment.verdict == Verdict.PASS
    assert "casual" in judgment.reasoning


def test_judge_parses_fail_verdict():
    provider = FakeLLMProvider('{"verdict": "FAIL", "reasoning": "Used a generic AI disclaimer."}')

    judgment = judge_persona_consistency(
        provider, DEFAULT_PERSONA, "Should not use generic AI disclaimers", "As an AI language model..."
    )

    assert judgment.verdict == Verdict.FAIL
