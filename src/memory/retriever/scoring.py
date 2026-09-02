from pydantic import BaseModel

from src.memory.decay.decay import recency_factor
from src.memory.models.memory import Memory
from src.memory.retriever.similarity import cosine_similarity

SIMILARITY_WEIGHT = 0.6
IMPORTANCE_WEIGHT = 0.2
CONFIDENCE_WEIGHT = 0.1
RECENCY_WEIGHT = 0.1


class ScoredMemory(BaseModel):
    memory: Memory
    semantic_similarity: float
    importance_weight: float
    recency_weight: float
    confidence_weight: float
    final_score: float


def score_memory(memory: Memory, query_vector: list[float]) -> ScoredMemory:
    similarity = cosine_similarity(query_vector, memory.embedding) if memory.embedding else 0.0
    recency = recency_factor(memory)

    final_score = (
        SIMILARITY_WEIGHT * similarity
        + IMPORTANCE_WEIGHT * memory.importance
        + CONFIDENCE_WEIGHT * memory.confidence
        + RECENCY_WEIGHT * recency
    )

    return ScoredMemory(
        memory=memory,
        semantic_similarity=similarity,
        importance_weight=memory.importance,
        recency_weight=recency,
        confidence_weight=memory.confidence,
        final_score=final_score,
    )
