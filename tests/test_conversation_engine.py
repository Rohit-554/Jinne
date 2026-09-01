from src.chat.conversation_engine import ConversationEngine
from src.memory.models.memory import MemoryStatus
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"


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
