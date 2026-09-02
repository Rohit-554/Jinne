from src.evaluation.baselines import BaselineBEngine, baseline_b_factory
from src.evaluation.runner import run_scenario
from src.evaluation.scenarios import Scenario, ScenarioCategory
from src.memory.models.memory import MemoryStatus
from src.memory.store.store import MemoryStore

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"


class RoutingFakeLLMProvider:
    def __init__(self, chat_reply: str, extraction_json_by_message: dict[str, str]):
        self._chat_reply = chat_reply
        self._extraction_json_by_message = extraction_json_by_message

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            user_message = messages[-1]["content"]
            return self._extraction_json_by_message[user_message]
        return self._chat_reply


class FakeEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


def test_baseline_b_never_supersedes_a_contradicted_fact():
    first_message = "I work at Google."
    second_message = "I left Google and joined Microsoft."
    provider = RoutingFakeLLMProvider(
        chat_reply="noted!",
        extraction_json_by_message={
            first_message: """{
                "candidates": [{
                    "decision": "SAVE", "type": "CAREER", "subject": "user",
                    "relation": "works_at", "value": "Google",
                    "importance": 0.9, "confidence": 0.95
                }]
            }""",
            second_message: """{
                "candidates": [{
                    "decision": "SAVE", "type": "CAREER", "subject": "user",
                    "relation": "works_at", "value": "Microsoft",
                    "importance": 0.9, "confidence": 0.95
                }]
            }""",
        },
    )
    store = MemoryStore(":memory:")
    try:
        engine = BaselineBEngine(provider, FakeEmbeddingProvider(), store)

        engine.handle_message(first_message)
        engine.handle_message(second_message)

        active = store.list(status=MemoryStatus.ACTIVE)
        assert len(active) == 2
        assert {m.value for m in active} == {"Google", "Microsoft"}
        assert all(m.supersedes_memory_id is None for m in active)
    finally:
        store.close()


def test_baseline_b_factory_persists_extracted_memories_via_run_scenario():
    message = "My dog's name is Bruno."
    provider = RoutingFakeLLMProvider(
        chat_reply="Bruno!",
        extraction_json_by_message={
            message: """{
                "candidates": [{
                    "decision": "SAVE", "type": "RELATIONSHIP", "subject": "user",
                    "relation": "pet_name", "value": "Bruno",
                    "importance": 0.8, "confidence": 0.95
                }]
            }""",
            "What is my dog's name?": '{"candidates": []}',
        },
    )
    scenario = Scenario(
        id="s1",
        category=ScenarioCategory.FACTUAL_RECALL,
        turns=[message],
        final_question="What is my dog's name?",
        expected_substring="Bruno",
    )

    response, store = run_scenario(scenario, provider, FakeEmbeddingProvider(), engine_factory=baseline_b_factory)

    try:
        assert response == "Bruno!"
        stored = store.list(status=MemoryStatus.ACTIVE)
        assert len(stored) == 1
        assert stored[0].value == "Bruno"
    finally:
        store.close()
