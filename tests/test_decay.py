from datetime import timedelta

from src.memory.decay.decay import DECAY_HALF_LIFE_DAYS, recency_factor
from src.memory.models.memory import Memory, MemoryType, utcnow


def _make_memory(memory_type: MemoryType, valid_from) -> Memory:
    return Memory(
        type=memory_type,
        subject="user",
        relation="r",
        value="v",
        importance=0.5,
        confidence=0.9,
        source_message_id="msg-1",
        valid_from=valid_from,
    )


def test_recency_factor_is_one_when_brand_new():
    memory = _make_memory(MemoryType.IDENTITY, utcnow())
    assert recency_factor(memory, now=memory.valid_from) == 1.0


def test_recency_factor_is_half_after_one_half_life():
    half_life = DECAY_HALF_LIFE_DAYS[MemoryType.TEMPORARY_STATE]
    now = utcnow()
    memory = _make_memory(MemoryType.TEMPORARY_STATE, now - timedelta(days=half_life))

    factor = recency_factor(memory, now=now)

    assert abs(factor - 0.5) < 1e-6


def test_temporary_state_decays_faster_than_identity_at_same_age():
    now = utcnow()
    age = timedelta(days=5)
    temp_memory = _make_memory(MemoryType.TEMPORARY_STATE, now - age)
    identity_memory = _make_memory(MemoryType.IDENTITY, now - age)

    assert recency_factor(temp_memory, now=now) < recency_factor(identity_memory, now=now)


def test_recency_factor_never_exceeds_one_for_future_valid_from():
    now = utcnow()
    memory = _make_memory(MemoryType.OTHER, now + timedelta(days=10))

    assert recency_factor(memory, now=now) == 1.0
