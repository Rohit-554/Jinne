import uuid

from src.chat.context_builder import build_messages
from src.llm.provider import EmbeddingProvider, LLMProvider
from src.memory.extractor.extractor import MemoryExtractor, extract_and_store
from src.memory.resolver.resolver import MemoryResolver
from src.memory.retriever.retriever import MemoryRetriever
from src.memory.store.store import MemoryStore
from src.persona.persona import Persona

RECENT_TURNS_WINDOW = 6
HISTORICAL_TOP_K = 2


class ConversationEngine:
    def __init__(
        self,
        llm: LLMProvider,
        embedder: EmbeddingProvider,
        store: MemoryStore,
        persona: Persona,
        retriever: MemoryRetriever | None = None,
        extractor: MemoryExtractor | None = None,
        resolver: MemoryResolver | None = None,
    ):
        self._llm = llm
        self._embedder = embedder
        self._store = store
        self._persona = persona
        self._retriever = retriever or MemoryRetriever(embedder, store)
        self._extractor = extractor or MemoryExtractor(llm)
        self._resolver = resolver or MemoryResolver(llm)
        self._recent_turns: list[tuple[str, str]] = []

    def handle_message(self, user_message: str) -> str:
        memories = self._retriever.retrieve(user_message)
        historical_memories = self._retriever.retrieve_historical(user_message, top_k=HISTORICAL_TOP_K)
        messages = build_messages(
            self._persona,
            memories,
            self._recent_turns,
            user_message,
            historical_memories=historical_memories,
        )
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
            resolver=self._resolver,
        )

        return response
