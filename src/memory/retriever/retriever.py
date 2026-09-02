from src.llm.provider import EmbeddingProvider
from src.memory.models.memory import Memory, MemoryStatus
from src.memory.retriever.scoring import ScoredMemory, score_memory
from src.memory.store.store import MemoryStore

DEFAULT_TOP_K = 5


class MemoryRetriever:
    def __init__(self, embedder: EmbeddingProvider, store: MemoryStore):
        self._embedder = embedder
        self._store = store

    def retrieve(self, message: str, top_k: int = DEFAULT_TOP_K) -> list[Memory]:
        scored = self._retrieve_scored_by_status(message, MemoryStatus.ACTIVE, top_k)
        return [s.memory for s in scored]

    def retrieve_historical(self, message: str, top_k: int = DEFAULT_TOP_K) -> list[Memory]:
        scored = self._retrieve_scored_by_status(message, MemoryStatus.SUPERSEDED, top_k)
        return [s.memory for s in scored]

    def retrieve_scored(self, message: str, top_k: int = DEFAULT_TOP_K) -> list[ScoredMemory]:
        return self._retrieve_scored_by_status(message, MemoryStatus.ACTIVE, top_k)

    def _retrieve_scored_by_status(self, message: str, status: MemoryStatus, top_k: int) -> list[ScoredMemory]:
        query_vector = self._embedder.embed(message)
        candidates = self._store.list(status=status)

        scored = [score_memory(memory, query_vector) for memory in candidates if memory.embedding is not None]
        scored.sort(key=lambda s: s.final_score, reverse=True)

        return scored[:top_k]
