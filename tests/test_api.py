from fastapi.testclient import TestClient

from src.api.app import app, get_engine
from src.chat.conversation_engine import ConversationEngine
from src.memory.models.memory import Memory, MemoryStatus, MemoryType
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"


class FakeStreamingLLMProvider:
    def __init__(self, chat_reply: str, extraction_json_by_message: dict[str, str]):
        self._chat_reply = chat_reply
        self._extraction_json_by_message = extraction_json_by_message

    def complete(self, messages: list[dict[str, str]]) -> str:
        system_content = messages[0]["content"]
        if system_content.startswith(EXTRACTION_SYSTEM_PREFIX):
            user_message = messages[-1]["content"]
            return self._extraction_json_by_message[user_message]
        return self._chat_reply

    def complete_stream(self, messages: list[dict[str, str]]):
        reply = self.complete(messages)
        for word in reply.split(" "):
            yield word + " "


class FakeEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


def _make_engine(tmp_path, chat_reply="Hi there!", extraction_by_message=None):
    store = MemoryStore(tmp_path / "companion.db")
    provider = FakeStreamingLLMProvider(chat_reply, extraction_by_message or {})
    engine = ConversationEngine(
        llm=provider,
        embedder=FakeEmbeddingProvider(),
        store=store,
        persona=DEFAULT_PERSONA,
    )
    return engine, store


def test_chat_endpoint_streams_chunks_and_final_metadata_event(tmp_path):
    message = "My dog's name is Bruno."
    engine, store = _make_engine(
        tmp_path,
        chat_reply="Bruno sounds lovely!",
        extraction_by_message={
            message: """{
                "candidates": [{
                    "decision": "SAVE", "type": "RELATIONSHIP", "subject": "user",
                    "relation": "pet_name", "value": "Bruno",
                    "importance": 0.8, "confidence": 0.95
                }]
            }"""
        },
    )
    try:
        app.dependency_overrides[get_engine] = lambda: engine
        client = TestClient(app)

        response = client.post("/api/chat", json={"message": message})

        assert response.status_code == 200
        body = response.text
        assert "event: chunk" in body
        assert "Bruno" in body
        assert "event: done" in body
        assert '"created_memories"' in body
        assert '"Bruno"' in body
    finally:
        app.dependency_overrides.clear()
        store.close()


def test_memories_endpoint_returns_only_active_memories(tmp_path):
    engine, store = _make_engine(tmp_path)
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

        app.dependency_overrides[get_engine] = lambda: engine
        client = TestClient(app)

        response = client.get("/api/memories")

        assert response.status_code == 200
        payload = response.json()
        values = [m["value"] for m in payload["memories"]]
        assert values == ["Microsoft"]
    finally:
        app.dependency_overrides.clear()
        store.close()


def test_memories_endpoint_excludes_embedding_field(tmp_path):
    embedder = FakeEmbeddingProvider()
    engine, store = _make_engine(tmp_path)
    try:
        store.save(
            Memory(
                type=MemoryType.CAREER,
                subject="user",
                relation="works_at",
                value="Google",
                status=MemoryStatus.ACTIVE,
                importance=0.9,
                confidence=0.95,
                source_message_id="msg-1",
                embedding=embedder.embed("works at Google"),
            )
        )

        app.dependency_overrides[get_engine] = lambda: engine
        client = TestClient(app)

        response = client.get("/api/memories")
        payload = response.json()

        assert "embedding" not in payload["memories"][0]
    finally:
        app.dependency_overrides.clear()
        store.close()
