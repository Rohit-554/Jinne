from collections import defaultdict

from src.memory.models.memory import Memory
from src.memory.retriever.scoring import ScoredMemory


def render_memory_timeline(memories: list[Memory]) -> str:
    if not memories:
        return "No memories stored yet."

    by_type: dict[str, list[Memory]] = defaultdict(list)
    for memory in memories:
        by_type[memory.type.value].append(memory)

    blocks = []
    for type_name in sorted(by_type):
        entries = sorted(by_type[type_name], key=lambda m: m.valid_from)
        lines = [type_name, ""]
        for entry in entries:
            lines.append(entry.valid_from.strftime("%b %Y"))
            lines.append(entry.value)
            lines.append(f"  status: {entry.status.value}")
            lines.append("")
        blocks.append("\n".join(lines).rstrip())

    return "\n\n".join(blocks)


def render_memory_debug(scored: list[ScoredMemory]) -> str:
    if not scored:
        return "No retrieval has happened yet - ask something first, then run /memory-debug."

    lines = ["Retrieved memories", ""]
    for i, entry in enumerate(scored, start=1):
        lines.append(f"{i}. {entry.memory.value}")
        lines.append(f"   semantic_similarity: {entry.semantic_similarity:.2f}")
        lines.append(f"   importance: {entry.importance_weight:.2f}")
        lines.append(f"   recency: {entry.recency_weight:.2f}")
        lines.append(f"   confidence: {entry.confidence_weight:.2f}")
        lines.append(f"   final_score: {entry.final_score:.2f}")
        lines.append("")

    return "\n".join(lines).rstrip()
