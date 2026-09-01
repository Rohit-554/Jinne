import pytest

from src.memory.models.memory import Memory, MemoryStatus, MemoryType
from src.memory.store.store import MemoryNotFoundError, MemoryStore


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


def test_update_status_mutates_in_place(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        saved = store.save(_make_memory())
        original_updated_at = saved.updated_at

        updated = store.update_status(saved.id, MemoryStatus.SUPERSEDED)

        assert updated.id == saved.id
        assert updated.type == saved.type
        assert updated.subject == saved.subject
        assert updated.relation == saved.relation
        assert updated.value == saved.value
        assert updated.status == MemoryStatus.SUPERSEDED
        assert updated.valid_until is None
        assert updated.updated_at >= original_updated_at

        fetched = store.get(saved.id)
        assert fetched.status == MemoryStatus.SUPERSEDED
    finally:
        store.close()


def test_update_status_sets_valid_until(tmp_path):
    from src.memory.models.memory import utcnow

    store = MemoryStore(tmp_path / "companion.db")
    try:
        saved = store.save(_make_memory())
        cutoff = utcnow()

        updated = store.update_status(saved.id, MemoryStatus.SUPERSEDED, valid_until=cutoff)

        assert updated.valid_until == cutoff
    finally:
        store.close()


def test_update_status_raises_for_unknown_id(tmp_path):
    store = MemoryStore(tmp_path / "companion.db")
    try:
        with pytest.raises(MemoryNotFoundError):
            store.update_status(999, MemoryStatus.SUPERSEDED)
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
