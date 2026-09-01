from src.memory.models.memory import Memory, MemoryStatus, MemoryType
from src.memory.store.store import MemoryStore


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


def test_save_and_get_round_trip(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        saved = store.save(_make_memory())
        assert saved.id is not None

        fetched = store.get(saved.id)
        assert fetched is not None
        assert fetched.id == saved.id
        assert fetched.type == MemoryType.CAREER
        assert fetched.subject == "user"
        assert fetched.relation == "works_at"
        assert fetched.value == "Microsoft"
        assert fetched.status == MemoryStatus.ACTIVE
        assert fetched.importance == 0.9
        assert fetched.confidence == 0.95
        assert fetched.source_message_id == "msg-1"
    finally:
        store.close()


def test_save_round_trips_embedding(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        saved = store.save(_make_memory(embedding=[0.1, 0.2, 0.3]))
        fetched = store.get(saved.id)
        assert fetched.embedding == [0.1, 0.2, 0.3]
    finally:
        store.close()


def test_list_filters_by_active_status(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        active = store.save(_make_memory(status=MemoryStatus.ACTIVE, source_message_id="msg-active"))
        store.save(_make_memory(status=MemoryStatus.SUPERSEDED, source_message_id="msg-superseded"))

        active_only = store.list(status=MemoryStatus.ACTIVE)

        assert [m.id for m in active_only] == [active.id]
        assert all(m.status == MemoryStatus.ACTIVE for m in active_only)
    finally:
        store.close()


def test_memory_persists_across_store_restart(tmp_path):
    db_path = tmp_path / "companion.db"

    store1 = MemoryStore(db_path)
    saved = store1.save(_make_memory(relation="works_at", value="Microsoft"))
    store1.close()

    store2 = MemoryStore(db_path)
    try:
        fetched = store2.get(saved.id)
        assert fetched is not None
        assert fetched.value == "Microsoft"
    finally:
        store2.close()
