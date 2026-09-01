import uuid

from src.chat.context_builder import build_messages
from src.llm.provider import EmbeddingProvider, LLMProvider
from src.memory.extractor.extractor import MemoryExtractor, extract_and_store
from src.memory.retriever.retriever import MemoryRetriever
from src.memory.store.store import MemoryStore
from src.persona.persona import Persona

RECENT_TURNS_WINDOW = 6


class ConversationEngine:
    def __init__(
        self,
        llm: LLMProvider,
        embedder: EmbeddingProvider,
        store: MemoryStore,
        persona: Persona,
        retriever: MemoryRetriever | None = None,
        extractor: MemoryExtractor | None = None,
    ):
        self._llm = llm
        self._embedder = embedder
        self._store = store
        self._persona = persona
        self._retriever = retriever or MemoryRetriever(embedder, store)
        self._extractor = extractor or MemoryExtractor(llm)
        self._recent_turns: list[tuple[str, str]] = []

    def handle_message(self, user_message: str) -> str:
        memories = self._retriever.retrieve(user_message)
        messages = build_messages(self._persona, memories, self._recent_turns, user_message)
        response = self._llm.complete(messages)

        self._recent_turns.append((user_message, response))
        self._recent_turns = self._recent_turns[-RECENT_TURNS_WINDOW:]

        message_id = str(uuid.uuid4())
        extract_and_store(
            self._extractor,
            self._store,
            user_message,
            message_id,
            embedder=self._embedder,
        )

        return response
