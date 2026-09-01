from src.evaluation.runner import run_scenario
from src.evaluation.scenarios import Scenario, ScenarioCategory
from src.memory.models.memory import MemoryStatus

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"


class OrderTrackingFakeLLMProvider:
    def __init__(self):
        self.chat_call_order: list[str] = []

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            return '{"candidates": []}'
        user_message = messages[-1]["content"]
        self.chat_call_order.append(user_message)
        return f"reply to: {user_message}"


class FakeEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


def test_run_scenario_sends_turns_in_order_before_final_question():
    provider = OrderTrackingFakeLLMProvider()
    scenario = Scenario(
        id="s1",
        category=ScenarioCategory.LONG_RANGE_RECALL,
        turns=["turn one", "turn two", "turn three"],
        final_question="final question",
        expected_substring="x",
    )

    response, store = run_scenario(scenario, provider, FakeEmbeddingProvider())

    assert provider.chat_call_order == ["turn one", "turn two", "turn three", "final question"]
    assert response == "reply to: final question"
    store.close()


class SavingFakeLLMProvider:
    """Extraction always saves one fact (a distinct relation per call, so
    the resolver never finds an existing match and skips its own LLM
    call) so we can check store isolation by counting saved memories."""

    def __init__(self):
        self.call_count = 0

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            self.call_count += 1
            return f"""{{
                "candidates": [
                    {{
                        "decision": "SAVE",
                        "type": "OTHER",
                        "subject": "user",
                        "relation": "fact_{self.call_count}",
                        "value": "value-{self.call_count}",
                        "importance": 0.7,
                        "confidence": 0.9
                    }}
                ]
            }}"""
        return "chat reply"


def test_run_scenario_stores_are_isolated_between_scenarios():
    provider = SavingFakeLLMProvider()
    embedder = FakeEmbeddingProvider()

    scenario1 = Scenario(
        id="s1",
        category=ScenarioCategory.FACTUAL_RECALL,
        turns=["some fact"],
        final_question="what did I say?",
        expected_substring="x",
    )
    scenario2 = Scenario(
        id="s2",
        category=ScenarioCategory.FACTUAL_RECALL,
        turns=[],
        final_question="what did I say?",
        expected_substring="x",
    )

    _, store1 = run_scenario(scenario1, provider, embedder)
    _, store2 = run_scenario(scenario2, provider, embedder)

    try:
        store1_memories = store1.list(status=MemoryStatus.ACTIVE)
        store2_memories = store2.list(status=MemoryStatus.ACTIVE)

        # scenario1 has 1 turn + 1 final question = 2 handle_message calls,
        # each extracting a SAVE candidate from this fake -> 2 memories.
        assert len(store1_memories) == 2
        # scenario2 has 0 turns + 1 final question = 1 handle_message call.
        # If store2 leaked scenario1's state it would have 3 memories, not 1.
        assert len(store2_memories) == 1
    finally:
        store1.close()
        store2.close()
