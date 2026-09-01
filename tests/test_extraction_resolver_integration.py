from src.memory.extractor.extractor import MemoryExtractor, extract_and_store
from src.memory.models.memory import Memory, MemoryStatus, MemoryType
from src.memory.resolver.resolver import MemoryResolver
from src.memory.store.store import MemoryStore

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"
RESOLVER_SYSTEM_PREFIX = "You are the memory-resolution module"


class RoutingFakeLLMProvider:
    def __init__(self, extraction_response: str, resolver_response: str):
        self._extraction_response = extraction_response
        self._resolver_response = resolver_response

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            return self._extraction_response
        assert system_content.startswith(RESOLVER_SYSTEM_PREFIX)
        return self._resolver_response


def test_career_change_supersedes_old_employer_end_to_end(tmp_path):
    message = "I left Google and joined Microsoft."
    store = MemoryStore(tmp_path / "companion.db")
    try:
        google = store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Google",
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-old",
            )
        )

        provider = RoutingFakeLLMProvider(
            extraction_response="""{
                "candidates": [
                    {
                        "decision": "SAVE",
                        "type": "CAREER",
                        "subject": "user",
                        "relation": "works_at",
                        "value": "Microsoft",
                        "importance": 0.9,
                        "confidence": 0.95
                    }
                ]
            }""",
            resolver_response=f'{{"action": "SUPERSEDE", "superseded_memory_id": {google.id}}}',
        )
        extractor = MemoryExtractor(provider)
        resolver = MemoryResolver(provider)

        saved = extract_and_store(
            extractor,
            store,
            message,
            source_message_id="msg-new",
            resolver=resolver,
        )

        assert len(saved) == 1
        assert saved[0].value == "Microsoft"
        assert saved[0].status == MemoryStatus.ACTIVE
        assert saved[0].supersedes_memory_id == google.id

        active = store.list(status=MemoryStatus.ACTIVE)
        assert [m.value for m in active] == ["Microsoft"]

        superseded = store.list(status=MemoryStatus.SUPERSEDED)
        assert [m.value for m in superseded] == ["Google"]
    finally:
        store.close()
