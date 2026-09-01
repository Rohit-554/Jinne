from src.memory.models.memory import Memory, MemoryType
from src.memory.retriever.embedding import embed_memory
from src.memory.store.store import MemoryStore


class FakeEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


def _make_memory(**overrides) -> Memory:
    defaults = dict(
        type=MemoryType.CAREER,
        subject="user",
        relation="works_at",
        value="Microsoft",
        importance=0.9,
        confidence=0.95,
        source_message_id="msg-1",
    )
    defaults.update(overrides)
    return Memory(**defaults)


def test_embed_memory_sets_embedding_field():
    memory = _make_memory()
    assert memory.embedding is None

    embedded = embed_memory(FakeEmbeddingProvider(), memory)

    assert embedded.embedding is not None
    assert len(embedded.embedding) == 3


def test_saved_memory_has_non_null_embedding(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        embedded = embed_memory(FakeEmbeddingProvider(), _make_memory())
        saved = store.save(embedded)

        assert saved.embedding is not None

        fetched = store.get(saved.id)
        assert fetched.embedding is not None
        assert fetched.embedding == saved.embedding
    finally:
        store.close()
