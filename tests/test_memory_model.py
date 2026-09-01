import pytest
from pydantic import ValidationError

from src.memory.models.memory import Memory, MemoryStatus, MemoryType


def test_memory_constructs_with_required_fields():
    memory = Memory(
        type=MemoryType.CAREER,
        subject="user",
        relation="works_at",
        value="Microsoft",
        importance=0.9,
        confidence=0.95,
        source_message_id="msg-1",
    )

    assert memory.id is None
    assert memory.status == MemoryStatus.ACTIVE
    assert memory.type == MemoryType.CAREER
    assert memory.embedding is None


def test_memory_rejects_missing_required_field():
    with pytest.raises(ValidationError):
        Memory(
            type=MemoryType.CAREER,
            subject="user",
            relation="works_at",
            # value is missing
            importance=0.9,
            confidence=0.95,
            source_message_id="msg-1",
        )
