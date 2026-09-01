from src.memory.models.memory import Memory

SYSTEM_PROMPT = """You are the memory-resolution module of a personal AI companion's memory system.

You are given a new candidate fact about the user, and a list of existing
memories that share the same subject and relation as the candidate. Decide
how the candidate relates to those existing memories:

- DUPLICATE: the candidate expresses the same fact as one of the existing
  memories (same meaning, possibly reworded). Set superseded_memory_id to
  that existing memory's id.
- SUPERSEDE: the candidate is a mutually exclusive replacement for one
  existing memory - it describes the current state now, replacing what
  used to be true, for a relation that can only hold one value at a time
  (e.g. where someone currently works, who they are currently dating,
  where they currently live). Set superseded_memory_id to the id of the
  existing memory it replaces.
- INDEPENDENT: the candidate can coexist with all the existing memories -
  the relation can legitimately hold multiple simultaneous values (e.g.
  foods or languages someone likes), or the candidate is meaningfully
  different despite sharing subject and relation. superseded_memory_id
  must be null.

Respond with ONLY a single JSON object (no markdown fences, no commentary)
matching exactly this shape:

{"action": "DUPLICATE" | "SUPERSEDE" | "INDEPENDENT", "superseded_memory_id": <int or null>}
"""


def build_messages(candidate_memory: Memory, existing_related_memories: list[Memory]) -> list[dict[str, str]]:
    existing_lines = "\n".join(f"- id={m.id}: {m.value}" for m in existing_related_memories)
    user_content = (
        f"New candidate fact: {candidate_memory.relation}: {candidate_memory.value}\n\n"
        f"Existing memories with the same subject and relation:\n{existing_lines}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
