from sqlalchemy import inspect

from src.memory.store.db import make_engine

EXPECTED_COLUMNS = {
    "id",
    "type",
    "subject",
    "relation",
    "value",
    "status",
    "importance",
    "confidence",
    "created_at",
    "updated_at",
    "valid_from",
    "valid_until",
    "supersedes_memory_id",
    "source_message_id",
    "embedding",
}


def test_make_engine_creates_memories_table_with_all_fields(tmp_path):
    db_path = tmp_path / "companion.db"
    engine = make_engine(db_path)

    inspector = inspect(engine)
    assert "memories" in inspector.get_table_names()

    columns = {col["name"] for col in inspector.get_columns("memories")}
    assert columns == EXPECTED_COLUMNS
