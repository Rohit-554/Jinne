import sys
import uuid

from src.chat.context_builder import build_messages
from src.llm.provider import EmbeddingProvider, LLMProvider
from src.memory.extractor.extractor import MemoryExtractor, extract_and_store
from src.memory.models.memory import Memory
from src.memory.resolver.resolver import MemoryResolver
from src.memory.retriever.retriever import MemoryRetriever
from src.memory.retriever.scoring import ScoredMemory
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
        self._last_scored_memories: list[ScoredMemory] = []

    def get_last_retrieval_debug(self) -> list[ScoredMemory]:
        return self._last_scored_memories

    def list_all_memories(self) -> list[Memory]:
        return self._store.list()

    def handle_message(self, user_message: str) -> str:
        scored_memories = self._retriever.retrieve_scored(user_message)
        self._last_scored_memories = scored_memories
        memories = [scored.memory for scored in scored_memories]
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
        try:
            extract_and_store(
                self._extractor,
                self._store,
                user_message,
                message_id,
                embedder=self._embedder,
                resolver=self._resolver,
            )
        except Exception as exc:
            print(f"[memory update failed, continuing conversation: {exc!r}]", file=sys.stderr)

        return response
