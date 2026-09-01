import json
from pathlib import Path

from src.memory.models.memory import Memory, MemoryStatus
from src.memory.store.db import make_engine, make_session_factory
from src.memory.store.schema import MemoryRow


class MemoryStore:
    def __init__(self, db_path: str | Path):
        self._engine = make_engine(db_path)
        self._session_factory = make_session_factory(self._engine)

    def close(self) -> None:
        self._engine.dispose()

    def save(self, memory: Memory) -> Memory:
        with self._session_factory() as session:
            row = MemoryRow(
                id=memory.id,
                type=memory.type,
                subject=memory.subject,
                relation=memory.relation,
                value=memory.value,
                status=memory.status,
                importance=memory.importance,
                confidence=memory.confidence,
                created_at=memory.created_at,
                updated_at=memory.updated_at,
                valid_from=memory.valid_from,
                valid_until=memory.valid_until,
                supersedes_memory_id=memory.supersedes_memory_id,
                source_message_id=memory.source_message_id,
                embedding=_encode_embedding(memory.embedding),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return _row_to_memory(row)

    def get(self, memory_id: int) -> Memory | None:
        with self._session_factory() as session:
            row = session.get(MemoryRow, memory_id)
            return _row_to_memory(row) if row else None

    def list(self, status: MemoryStatus | None = None) -> list[Memory]:
        with self._session_factory() as session:
            query = session.query(MemoryRow)
            if status is not None:
                query = query.filter(MemoryRow.status == status)
            return [_row_to_memory(row) for row in query.all()]


def _encode_embedding(embedding: list[float] | None) -> str | None:
    return json.dumps(embedding) if embedding is not None else None


def _decode_embedding(embedding: str | None) -> list[float] | None:
    return json.loads(embedding) if embedding else None


def _row_to_memory(row: MemoryRow) -> Memory:
    return Memory(
        id=row.id,
        type=row.type,
        subject=row.subject,
        relation=row.relation,
        value=row.value,
        status=row.status,
        importance=row.importance,
        confidence=row.confidence,
        created_at=row.created_at,
        updated_at=row.updated_at,
        valid_from=row.valid_from,
        valid_until=row.valid_until,
        supersedes_memory_id=row.supersedes_memory_id,
        source_message_id=row.source_message_id,
        embedding=_decode_embedding(row.embedding),
    )
