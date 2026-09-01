from src.llm.provider import EmbeddingProvider
from src.memory.models.memory import Memory, MemoryStatus
from src.memory.retriever.similarity import cosine_similarity
from src.memory.store.store import MemoryStore

DEFAULT_TOP_K = 5


class MemoryRetriever:
    def __init__(self, embedder: EmbeddingProvider, store: MemoryStore):
        self._embedder = embedder
        self._store = store

    def retrieve(self, message: str, top_k: int = DEFAULT_TOP_K) -> list[Memory]:
        return self._retrieve_by_status(message, MemoryStatus.ACTIVE, top_k)

    def retrieve_historical(self, message: str, top_k: int = DEFAULT_TOP_K) -> list[Memory]:
        return self._retrieve_by_status(message, MemoryStatus.SUPERSEDED, top_k)

    def _retrieve_by_status(self, message: str, status: MemoryStatus, top_k: int) -> list[Memory]:
        query_vector = self._embedder.embed(message)
        candidates = self._store.list(status=status)

        scored = [
            (memory, cosine_similarity(query_vector, memory.embedding))
            for memory in candidates
            if memory.embedding is not None
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        return [memory for memory, _ in scored[:top_k]]
