from src.chat.conversation_engine import ConversationEngine
from src.memory.models.memory import Memory, MemoryStatus, MemoryType
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"
RESOLVER_SYSTEM_PREFIX = "You are the memory-resolution module"


class RoutingFakeLLMProvider:
    """Routes to a canned chat reply or a canned extraction JSON response
    based on which system prompt the caller used, so a single fake can
    stand in for both the chat and extraction call sites."""

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


class CapturingFakeLLMProvider:
    """Routes to a canned chat reply, extraction JSON, or resolver JSON
    based on the system prompt, and records the messages used for the
    chat call so the test can inspect what reached the model."""

    def __init__(self, chat_reply: str, extraction_json_by_message: dict[str, str]):
        self._chat_reply = chat_reply
        self._extraction_json_by_message = extraction_json_by_message
        self.chat_messages: list[dict[str, str]] | None = None

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            user_message = messages[-1]["content"]
            return self._extraction_json_by_message[user_message]
        if system_content.startswith(RESOLVER_SYSTEM_PREFIX):
            return '{"action": "INDEPENDENT", "superseded_memory_id": null}'
        self.chat_messages = messages
        return self._chat_reply


def test_handle_message_returns_chat_reply_and_stores_extracted_fact(tmp_path):
    user_message = "My dog's name is Bruno."
    provider = RoutingFakeLLMProvider(
        chat_reply="Bruno sounds like a good boy!",
        extraction_json_by_message={
            user_message: """{
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
        },
    )
    store = MemoryStore(tmp_path / "companion.db")
    try:
        engine = ConversationEngine(
            llm=provider,
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        response = engine.handle_message(user_message)

        assert response == "Bruno sounds like a good boy!"

        stored = store.list(status=MemoryStatus.ACTIVE)
        assert len(stored) == 1
        assert stored[0].value == "Bruno"
        assert stored[0].embedding is not None
    finally:
        store.close()


def test_handle_message_includes_historical_memory_in_prompt(tmp_path):
    embedder = FakeEmbeddingProvider()
    store = MemoryStore(tmp_path / "companion.db")
    try:
        store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Google",
                status=MemoryStatus.SUPERSEDED,
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-old",
                embedding=embedder.embed("works at Google"),
            )
        )

        user_message = "Where did I work before?"
        provider = CapturingFakeLLMProvider(
            chat_reply="You worked at Google before your current job!",
            extraction_json_by_message={user_message: '{"candidates": []}'},
        )
        engine = ConversationEngine(llm=provider, embedder=embedder, store=store, persona=DEFAULT_PERSONA)

        response = engine.handle_message(user_message)

        assert response == "You worked at Google before your current job!"
        assert provider.chat_messages is not None
        system_content = provider.chat_messages[0]["content"]
        assert "RELEVANT HISTORICAL MEMORY" in system_content
        assert "Google" in system_content
    finally:
        store.close()


class BrokenExtractionLLMProvider:
    """Returns a normal chat reply, but garbage JSON for extraction, to
    simulate a malformed/unreliable LLM response during memory
    processing."""

    def __init__(self, chat_reply: str):
        self._chat_reply = chat_reply

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            return "not valid json at all"
        return self._chat_reply


def test_handle_message_still_returns_reply_when_memory_processing_fails(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        provider = BrokenExtractionLLMProvider(chat_reply="Still here for you!")
        engine = ConversationEngine(
            llm=provider,
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        response = engine.handle_message("this will fail to extract")

        assert response == "Still here for you!"
        assert store.list() == []
    finally:
        store.close()


def test_get_last_retrieval_debug_empty_before_any_turn(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        engine = ConversationEngine(
            llm=RoutingFakeLLMProvider(chat_reply="hi", extraction_json_by_message={}),
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        assert engine.get_last_retrieval_debug() == []
    finally:
        store.close()


def test_get_last_retrieval_debug_reflects_last_turns_retrieval(tmp_path):
    embedder = FakeEmbeddingProvider()
    store = MemoryStore(tmp_path / "companion.db")
    try:
        saved = store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Microsoft",
                status=MemoryStatus.ACTIVE,
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-old",
                embedding=embedder.embed("works at Microsoft"),
            )
        )

        user_message = "Where do I work?"
        provider = RoutingFakeLLMProvider(
            chat_reply="Microsoft!",
            extraction_json_by_message={user_message: '{"candidates": []}'},
        )
        engine = ConversationEngine(llm=provider, embedder=embedder, store=store, persona=DEFAULT_PERSONA)

        engine.handle_message(user_message)
        debug = engine.get_last_retrieval_debug()

        assert len(debug) == 1
        assert debug[0].memory.id == saved.id
        assert debug[0].final_score is not None
    finally:
        store.close()


class RoutingFakeStreamingLLMProvider(RoutingFakeLLMProvider):
    """Same routing as RoutingFakeLLMProvider, plus complete_stream that
    yields the chat reply in a few chunks."""

    def complete_stream(self, messages: list[dict[str, str]]):
        reply = self.complete(messages)
        chunk_size = max(1, len(reply) // 3)
        for i in range(0, len(reply), chunk_size):
            yield reply[i : i + chunk_size]


def test_handle_message_stream_yields_chunks_that_concatenate_to_full_reply(tmp_path):
    user_message = "My dog's name is Bruno."
    provider = RoutingFakeStreamingLLMProvider(
        chat_reply="Bruno sounds like a good boy!",
        extraction_json_by_message={user_message: '{"candidates": []}'},
    )
    store = MemoryStore(tmp_path / "companion.db")
    try:
        engine = ConversationEngine(
            llm=provider,
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        chunks = list(engine.handle_message_stream(user_message))

        assert len(chunks) > 1
        assert "".join(chunks) == "Bruno sounds like a good boy!"
    finally:
        store.close()


def test_handle_message_stream_still_finalizes_turn_after_streaming(tmp_path):
    user_message = "My dog's name is Bruno."
    provider = RoutingFakeStreamingLLMProvider(
        chat_reply="Bruno!",
        extraction_json_by_message={
            user_message: """{
                "candidates": [{
                    "decision": "SAVE", "type": "RELATIONSHIP", "subject": "user",
                    "relation": "pet_name", "value": "Bruno",
                    "importance": 0.8, "confidence": 0.95
                }]
            }"""
        },
    )
    store = MemoryStore(tmp_path / "companion.db")
    try:
        engine = ConversationEngine(
            llm=provider,
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        list(engine.handle_message_stream(user_message))

        stored = store.list(status=MemoryStatus.ACTIVE)
        assert len(stored) == 1
        assert stored[0].value == "Bruno"
    finally:
        store.close()


def test_handle_message_stream_raises_for_non_streaming_provider(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        engine = ConversationEngine(
            llm=RoutingFakeLLMProvider(chat_reply="hi", extraction_json_by_message={}),
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        try:
            engine.handle_message_stream("hello")
            assert False, "expected TypeError"
        except TypeError:
            pass
    finally:
        store.close()


def test_get_last_turn_memory_changes_empty_before_any_turn(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        engine = ConversationEngine(
            llm=RoutingFakeLLMProvider(chat_reply="hi", extraction_json_by_message={}),
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        created, updated = engine.get_last_turn_memory_changes()
        assert created == []
        assert updated == []
    finally:
        store.close()


def test_get_last_turn_memory_changes_reflects_a_supersede(tmp_path):
    embedder = FakeEmbeddingProvider()
    store = MemoryStore(tmp_path / "companion.db")
    try:
        google = store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Google",
                status=MemoryStatus.ACTIVE,
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-old",
                embedding=embedder.embed("works at Google"),
            )
        )

        user_message = "I left Google and joined Microsoft."
        provider = RoutingFakeLLMProvider(
            chat_reply="Congrats on the new job!",
            extraction_json_by_message={
                user_message: """{
                    "candidates": [{
                        "decision": "SAVE", "type": "CAREER", "subject": "user",
                        "relation": "works_at", "value": "Microsoft",
                        "importance": 0.9, "confidence": 0.95
                    }]
                }"""
            },
        )

        class ResolverProvider:
            def complete(self, messages):
                system_content = messages[0]["content"]
                if system_content.startswith(RESOLVER_SYSTEM_PREFIX):
                    return f'{{"action": "SUPERSEDE", "superseded_memory_id": {google.id}}}'
                return provider.complete(messages)

        engine = ConversationEngine(
            llm=ResolverProvider(), embedder=embedder, store=store, persona=DEFAULT_PERSONA
        )

        engine.handle_message(user_message)
        created, updated = engine.get_last_turn_memory_changes()

        assert [m.value for m in created] == ["Microsoft"]
        assert [m.value for m in updated] == ["Google"]
        assert updated[0].status == MemoryStatus.SUPERSEDED
    finally:
        store.close()


def test_list_all_memories_returns_every_status(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Google",
                status=MemoryStatus.SUPERSEDED,
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-1",
            )
        )
        store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Microsoft",
                status=MemoryStatus.ACTIVE,
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-2",
            )
        )

        engine = ConversationEngine(
            llm=RoutingFakeLLMProvider(chat_reply="hi", extraction_json_by_message={}),
            embedder=FakeEmbeddingProvider(),
            store=store,
            persona=DEFAULT_PERSONA,
        )

        all_memories = engine.list_all_memories()

        assert {m.value for m in all_memories} == {"Google", "Microsoft"}
        assert {m.status for m in all_memories} == {MemoryStatus.SUPERSEDED, MemoryStatus.ACTIVE}
    finally:
        store.close()
