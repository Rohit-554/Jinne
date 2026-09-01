from src.memory.models.memory import Memory, MemoryStatus, MemoryType
from src.memory.resolver.resolver import MemoryResolver
from src.memory.store.store import MemoryStore


class FakeLLMProvider:
    def __init__(self, response: str):
        self._response = response
        self.call_count = 0

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.call_count += 1
        return self._response


def _candidate(**overrides) -> Memory:
    defaults = dict(
        type=MemoryType.CAREER,
        subject="user",
        relation="works_at",
        value="Microsoft",
        importance=0.9,
        confidence=0.95,
        source_message_id="msg-new",
    )
    defaults.update(overrides)
    return Memory(**defaults)


def test_new_independent_fact_when_nothing_existing_matches(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        provider = FakeLLMProvider('{"action": "INDEPENDENT", "superseded_memory_id": null}')
        resolver = MemoryResolver(provider)

        result = resolver.resolve(_candidate(), store)

        assert result is not None
        assert result.status == MemoryStatus.ACTIVE
        assert result.supersedes_memory_id is None
        assert provider.call_count == 0  # nothing to compare against, no LLM call
    finally:
        store.close()


def test_duplicate_produces_no_new_memory(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        existing = store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Microsoft",
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-old",
            )
        )
        provider = FakeLLMProvider(
            f'{{"action": "DUPLICATE", "superseded_memory_id": {existing.id}}}'
        )
        resolver = MemoryResolver(provider)

        result = resolver.resolve(_candidate(), store)

        assert result is None
        unchanged = store.get(existing.id)
        assert unchanged.status == MemoryStatus.ACTIVE
    finally:
        store.close()


def test_supersede_marks_old_memory_superseded_and_links_new_one(tmp_path):
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
        provider = FakeLLMProvider(f'{{"action": "SUPERSEDE", "superseded_memory_id": {google.id}}}')
        resolver = MemoryResolver(provider)

        result = resolver.resolve(_candidate(value="Microsoft"), store)

        assert result is not None
        assert result.status == MemoryStatus.ACTIVE
        assert result.supersedes_memory_id == google.id

        saved = store.save(result)
        stored_google = store.get(google.id)
        assert stored_google.status == MemoryStatus.SUPERSEDED
        assert stored_google.valid_until is not None
        assert saved.status == MemoryStatus.ACTIVE
        assert saved.supersedes_memory_id == google.id
    finally:
        store.close()


def test_independent_fact_does_not_touch_existing_related_memory(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        kotlin = store.save(
            Memory(
                type=MemoryType.PREFERENCE,
                subject="user",
                relation="likes_language",
                value="Kotlin",
                importance=0.6,
                confidence=0.9,
                source_message_id="msg-old",
            )
        )
        provider = FakeLLMProvider('{"action": "INDEPENDENT", "superseded_memory_id": null}')
        resolver = MemoryResolver(provider)

        result = resolver.resolve(
            _candidate(type=MemoryType.PREFERENCE, relation="likes_language", value="Python"),
            store,
        )

        assert result is not None
        assert result.status == MemoryStatus.ACTIVE
        assert result.supersedes_memory_id is None
        assert store.get(kotlin.id).status == MemoryStatus.ACTIVE
    finally:
        store.close()


def test_low_confidence_candidate_is_uncertain_without_classification_call(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        store.save(
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
        provider = FakeLLMProvider("SHOULD NOT BE CALLED")
        resolver = MemoryResolver(provider)

        result = resolver.resolve(_candidate(value="Microsoft", confidence=0.4), store)

        assert result is not None
        assert result.status == MemoryStatus.UNCERTAIN
        assert provider.call_count == 0

        existing = store.list(status=MemoryStatus.ACTIVE)
        assert len(existing) == 1
        assert existing[0].value == "Google"
    finally:
        store.close()
