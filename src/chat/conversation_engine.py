import sys
import uuid
from collections.abc import Iterator

from src.chat.context_builder import build_messages
from src.llm.provider import EmbeddingProvider, LLMProvider, StreamingLLMProvider
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
        self._last_created_memories: list[Memory] = []

    def get_last_retrieval_debug(self) -> list[ScoredMemory]:
        return self._last_scored_memories

    def get_last_turn_memory_changes(self) -> tuple[list[Memory], list[Memory]]:
        created = self._last_created_memories
        updated: list[Memory] = []
        for memory in created:
            if memory.supersedes_memory_id is not None:
                old = self._store.get(memory.supersedes_memory_id)
                if old is not None:
                    updated.append(old)
        return created, updated

    def list_all_memories(self) -> list[Memory]:
        return self._store.list()

    def _prepare_turn(self, user_message: str) -> list[dict[str, str]]:
        scored_memories = self._retriever.retrieve_scored(user_message)
        self._last_scored_memories = scored_memories
        memories = [scored.memory for scored in scored_memories]
        historical_memories = self._retriever.retrieve_historical(user_message, top_k=HISTORICAL_TOP_K)
        return build_messages(
            self._persona,
            memories,
            self._recent_turns,
            user_message,
            historical_memories=historical_memories,
        )

    def _finalize_turn(self, user_message: str, response: str) -> None:
        self._recent_turns.append((user_message, response))
        self._recent_turns = self._recent_turns[-RECENT_TURNS_WINDOW:]

        message_id = str(uuid.uuid4())
        self._last_created_memories = []
        try:
            self._last_created_memories = extract_and_store(
                self._extractor,
                self._store,
                user_message,
                message_id,
                embedder=self._embedder,
                resolver=self._resolver,
            )
        except Exception as exc:
            print(f"[memory update failed, continuing conversation: {exc!r}]", file=sys.stderr)

    def handle_message(self, user_message: str) -> str:
        messages = self._prepare_turn(user_message)
        response = self._llm.complete(messages)
        self._finalize_turn(user_message, response)
        return response

    def handle_message_stream(self, user_message: str) -> Iterator[str]:
        if not isinstance(self._llm, StreamingLLMProvider):
            raise TypeError("The configured LLM provider does not support streaming")

        messages = self._prepare_turn(user_message)
        return self._stream_and_finalize(user_message, messages)

    def _stream_and_finalize(self, user_message: str, messages: list[dict[str, str]]) -> Iterator[str]:
        chunks: list[str] = []
        for chunk in self._llm.complete_stream(messages):
            chunks.append(chunk)
            yield chunk
        self._finalize_turn(user_message, "".join(chunks))
