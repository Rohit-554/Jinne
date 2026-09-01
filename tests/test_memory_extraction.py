from src.memory.extractor.extractor import MemoryExtractor, extract_and_store
from src.memory.extractor.schemas import ExtractionDecision
from src.memory.models.memory import MemoryStatus, MemoryType
from src.memory.store.store import MemoryStore


class FakeLLMProvider:
    def __init__(self, response_by_message: dict[str, str]):
        self._response_by_message = response_by_message

    def complete(self, messages: list[dict[str, str]]) -> str:
        user_message = messages[-1]["content"]
        return self._response_by_message[user_message]


def test_stable_fact_yields_save_candidate():
    message = "My dog's name is Bruno."
    provider = FakeLLMProvider(
        {
            message: """{
                "candidates": [
                    {
                        "decision": "SAVE",
                        "type": "RELATIONSHIP",
                        "subject": "user",
                        "relation": "pet_name",
                        "value": "Bruno",
                        "importance": 0.8,
                        "confidence": 0.95
                    }
                ]
            }"""
        }
    )
    extractor = MemoryExtractor(provider)

    candidates = extractor.extract(message)

    assert len(candidates) == 1
    assert candidates[0].decision == ExtractionDecision.SAVE
    assert candidates[0].value == "Bruno"


def test_greeting_and_trivial_state_yield_no_save_candidates():
    provider = FakeLLMProvider(
        {
            "hi": '{"candidates": []}',
            "I'm eating pizza right now": '{"candidates": []}',
        }
    )
    extractor = MemoryExtractor(provider)

    assert [c for c in extractor.extract("hi") if c.decision == ExtractionDecision.SAVE] == []
    assert [
        c for c in extractor.extract("I'm eating pizza right now") if c.decision == ExtractionDecision.SAVE
    ] == []


def test_message_with_two_facts_yields_two_save_candidates():
    message = "I finally joined Microsoft as an Android engineer."
    provider = FakeLLMProvider(
        {
            message: """{
                "candidates": [
                    {
                        "decision": "SAVE",
                        "type": "CAREER",
                        "subject": "user",
                        "relation": "works_at",
                        "value": "Microsoft",
                        "importance": 0.9,
                        "confidence": 0.95
                    },
                    {
                        "decision": "SAVE",
                        "type": "CAREER",
                        "subject": "user",
                        "relation": "job_role",
                        "value": "Android Engineer",
                        "importance": 0.85,
                        "confidence": 0.9
                    }
                ]
            }"""
        }
    )
    extractor = MemoryExtractor(provider)

    candidates = extractor.extract(message)

    assert len(candidates) == 2
    assert {(c.relation, c.value) for c in candidates} == {
        ("works_at", "Microsoft"),
        ("job_role", "Android Engineer"),
    }


def test_extract_and_store_persists_only_save_candidates(tmp_path):
    message = "I left Google and joined Microsoft."
    provider = FakeLLMProvider(
        {
            message: """{
                "candidates": [
                    {
                        "decision": "SAVE",
                        "type": "CAREER",
                        "subject": "user",
                        "relation": "works_at",
                        "value": "Microsoft",
                        "importance": 0.9,
                        "confidence": 0.95
                    },
                    {"decision": "IGNORE"}
                ]
            }"""
        }
    )
    extractor = MemoryExtractor(provider)
    store = MemoryStore(tmp_path / "companion.db")
    try:
        saved = extract_and_store(extractor, store, message, source_message_id="msg-42")

        assert len(saved) == 1
        assert saved[0].value == "Microsoft"
        assert saved[0].status == MemoryStatus.ACTIVE
        assert saved[0].source_message_id == "msg-42"

        stored = store.list(status=MemoryStatus.ACTIVE)
        assert len(stored) == 1
        assert stored[0].type == MemoryType.CAREER
        assert stored[0].value == "Microsoft"
    finally:
        store.close()
