from datetime import datetime

from src.memory.models.memory import Memory, MemoryType, utcnow

DECAY_HALF_LIFE_DAYS: dict[MemoryType, float] = {
    MemoryType.TEMPORARY_STATE: 1.0,
    MemoryType.EVENT: 14.0,
    MemoryType.PLAN: 30.0,
    MemoryType.GOAL: 180.0,
    MemoryType.EXPERIENCE: 365.0,
    MemoryType.PREFERENCE: 1825.0,
    MemoryType.CAREER: 1825.0,
    MemoryType.LOCATION: 1825.0,
    MemoryType.IDENTITY: 3650.0,
    MemoryType.RELATIONSHIP: 3650.0,
    MemoryType.PERSON: 3650.0,
    MemoryType.OTHER: 365.0,
}

DEFAULT_HALF_LIFE_DAYS = 365.0


def recency_factor(memory: Memory, now: datetime | None = None) -> float:
    now = now or utcnow()
    half_life = DECAY_HALF_LIFE_DAYS.get(memory.type, DEFAULT_HALF_LIFE_DAYS)
    age_days = max((now - memory.valid_from).total_seconds() / 86400.0, 0.0)
    return 0.5 ** (age_days / half_life)
