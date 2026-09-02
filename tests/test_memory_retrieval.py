import pytest

from src.llm.fastembed_provider import FastEmbedProvider
from src.memory.models.memory import Memory, MemoryStatus, MemoryType
from src.memory.retriever.embedding import embed_memory
from src.memory.retriever.retriever import MemoryRetriever
from src.memory.retriever.similarity import cosine_similarity
from src.memory.store.store import MemoryStore

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


@pytest.fixture(scope="module")
def embedder():
    return FastEmbedProvider(model_name=EMBEDDING_MODEL)


def _seed(store: MemoryStore, embedder, *, relation: str, value: str, status: MemoryStatus = MemoryStatus.ACTIVE):
    memory = Memory(
        type=MemoryType.OTHER,
        subject="user",
        relation=relation,
        value=value,
        status=status,
        importance=0.7,
        confidence=0.9,
        source_message_id="msg-seed",
    )
    return store.save(embed_memory(embedder, memory))


def test_retrieve_returns_results_ordered_by_descending_similarity(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        _seed(store, embedder, relation="pet_name", value="Bruno")
        _seed(store, embedder, relation="likes_language", value="Kotlin")
        _seed(store, embedder, relation="upcoming_event", value="Stripe interview tomorrow")
        _seed(store, embedder, relation="prefers_drink", value="tea")

        retriever = MemoryRetriever(embedder, store)
        results = retriever.retrieve("I'm really nervous about tomorrow", top_k=4)

        query_vector = embedder.embed("I'm really nervous about tomorrow")
        scores = [cosine_similarity(query_vector, m.embedding) for m in results]
        assert scores == sorted(scores, reverse=True)
    finally:
        store.close()


def test_retrieve_result_is_bounded_by_top_k(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        for i in range(6):
            _seed(store, embedder, relation=f"fact_{i}", value=f"Fact number {i}")

        retriever = MemoryRetriever(embedder, store)
        results = retriever.retrieve("Tell me a fact", top_k=2)

        assert len(results) == 2
    finally:
        store.close()


def test_retrieve_excludes_non_active_memories(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        _seed(
            store,
            embedder,
            relation="upcoming_event",
            value="Stripe interview tomorrow",
            status=MemoryStatus.SUPERSEDED,
        )

        retriever = MemoryRetriever(embedder, store)
        results = retriever.retrieve("Stripe interview tomorrow", top_k=5)

        assert results == []
    finally:
        store.close()


def test_retrieve_finds_semantically_related_memory_without_keyword_overlap(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        _seed(store, embedder, relation="pet_name", value="Bruno")
        _seed(store, embedder, relation="likes_language", value="Kotlin")
        target = _seed(store, embedder, relation="upcoming_event", value="Stripe interview tomorrow")
        _seed(store, embedder, relation="prefers_drink", value="tea")

        retriever = MemoryRetriever(embedder, store)
        results = retriever.retrieve("I'm really nervous about tomorrow", top_k=1)

        assert len(results) == 1
        assert results[0].id == target.id
    finally:
        store.close()


def test_retrieve_historical_returns_only_superseded_memories_ordered_by_similarity(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        _seed(store, embedder, relation="works_at", value="Microsoft", status=MemoryStatus.ACTIVE)
        _seed(store, embedder, relation="works_at", value="Google", status=MemoryStatus.SUPERSEDED)
        _seed(store, embedder, relation="pet_name", value="Bruno", status=MemoryStatus.SUPERSEDED)

        retriever = MemoryRetriever(embedder, store)
        results = retriever.retrieve_historical("Where did I work before Microsoft?", top_k=5)

        assert all(m.status == MemoryStatus.SUPERSEDED for m in results)
        assert "Google" in [m.value for m in results]
        assert "Microsoft" not in [m.value for m in results]

        query_vector = embedder.embed("Where did I work before Microsoft?")
        scores = [cosine_similarity(query_vector, m.embedding) for m in results]
        assert scores == sorted(scores, reverse=True)
    finally:
        store.close()


def test_retrieve_historical_is_bounded_by_top_k(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        for i in range(6):
            _seed(store, embedder, relation=f"fact_{i}", value=f"Fact number {i}", status=MemoryStatus.SUPERSEDED)

        retriever = MemoryRetriever(embedder, store)
        results = retriever.retrieve_historical("Tell me a fact", top_k=2)

        assert len(results) == 2
    finally:
        store.close()


def test_retrieve_historical_returns_empty_when_no_superseded_memories(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        _seed(store, embedder, relation="works_at", value="Microsoft", status=MemoryStatus.ACTIVE)

        retriever = MemoryRetriever(embedder, store)
        results = retriever.retrieve_historical("Where did I work before?", top_k=5)

        assert results == []
    finally:
        store.close()


def test_retrieve_scored_returns_full_breakdown_per_candidate(tmp_path, embedder):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        _seed(store, embedder, relation="pet_name", value="Bruno")
        _seed(store, embedder, relation="upcoming_event", value="Stripe interview tomorrow")

        retriever = MemoryRetriever(embedder, store)
        scored = retriever.retrieve_scored("I'm nervous about tomorrow", top_k=2)

        assert len(scored) == 2
        for entry in scored:
            assert 0.0 <= entry.importance_weight <= 1.0
            assert 0.0 <= entry.confidence_weight <= 1.0
            assert 0.0 <= entry.recency_weight <= 1.0
            assert isinstance(entry.final_score, float)
        scores = [entry.final_score for entry in scored]
        assert scores == sorted(scores, reverse=True)
    finally:
        store.close()
