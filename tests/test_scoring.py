from src.memory.models.memory import Memory, MemoryType
from src.memory.retriever.scoring import (
    CONFIDENCE_WEIGHT,
    IMPORTANCE_WEIGHT,
    RECENCY_WEIGHT,
    SIMILARITY_WEIGHT,
    score_memory,
)


def _make_memory(**overrides) -> Memory:
    defaults = dict(
        type=MemoryType.IDENTITY,
        subject="user",
        relation="r",
        value="v",
        importance=0.5,
        confidence=0.9,
        source_message_id="msg-1",
        embedding=[1.0, 0.0],
    )
    defaults.update(overrides)
    return Memory(**defaults)


def test_score_memory_includes_all_components():
    memory = _make_memory()
    scored = score_memory(memory, query_vector=[1.0, 0.0])

    assert scored.semantic_similarity == 1.0
    assert scored.importance_weight == memory.importance
    assert scored.confidence_weight == memory.confidence
    assert 0.0 <= scored.recency_weight <= 1.0

    expected = (
        SIMILARITY_WEIGHT * scored.semantic_similarity
        + IMPORTANCE_WEIGHT * scored.importance_weight
        + CONFIDENCE_WEIGHT * scored.confidence_weight
        + RECENCY_WEIGHT * scored.recency_weight
    )
    assert abs(scored.final_score - expected) < 1e-9


def test_higher_importance_can_outrank_slightly_higher_similarity():
    low_importance_high_similarity = _make_memory(importance=0.1, confidence=0.5)
    high_importance_slightly_lower_similarity = _make_memory(importance=0.95, confidence=0.5)

    query_vector = [1.0, 0.0]
    scored_a = score_memory(low_importance_high_similarity, query_vector)
    # Simulate a slightly lower similarity by using a query vector that is
    # not perfectly aligned but close.
    scored_b = score_memory(high_importance_slightly_lower_similarity, [0.99, 0.14])

    assert scored_b.final_score > scored_a.final_score


def test_score_memory_handles_missing_embedding_as_zero_similarity():
    memory = _make_memory(embedding=None)
    scored = score_memory(memory, query_vector=[1.0, 0.0])

    assert scored.semantic_similarity == 0.0
