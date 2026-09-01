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
        query_vector = self._embedder.embed(message)
        active_memories = self._store.list(status=MemoryStatus.ACTIVE)

        scored = [
            (memory, cosine_similarity(query_vector, memory.embedding))
            for memory in active_memories
            if memory.embedding is not None
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        return [memory for memory, _ in scored[:top_k]]
