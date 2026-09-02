from src.memory.models.memory import Memory


def memory_summary(memory: Memory) -> dict:
    return {
        "id": memory.id,
        "type": memory.type.value,
        "subject": memory.subject,
        "relation": memory.relation,
        "value": memory.value,
        "status": memory.status.value,
        "importance": memory.importance,
        "confidence": memory.confidence,
    }
