from src.memory.models.memory import Memory
from src.persona.persona import Persona
from src.persona.render import render_persona


def build_messages(
    persona: Persona,
    memories: list[Memory],
    recent_turns: list[tuple[str, str]],
    user_message: str,
    historical_memories: list[Memory] | None = None,
) -> list[dict[str, str]]:
    persona_block = render_persona(persona)

    if memories:
        memory_lines = "\n".join(f"- {m.relation.replace('_', ' ')}: {m.value}" for m in memories)
    else:
        memory_lines = "(none)"
    memory_block = f"RELEVANT USER MEMORY\n{memory_lines}"

    blocks = [persona_block, memory_block]

    instruction = (
        "Respond to the user in character. Weave in relevant memory only "
        "when it naturally fits; do not recite it as a list."
    )

    if historical_memories:
        historical_lines = "\n".join(
            f"- {m.relation.replace('_', ' ')}: {m.value} (no longer current)" for m in historical_memories
        )
        blocks.append(f"RELEVANT HISTORICAL MEMORY (past state, not current)\n{historical_lines}")
        instruction += (
            " Treat RELEVANT HISTORICAL MEMORY as past state only - never "
            "present it as true now."
        )

    system_content = "\n\n".join(blocks) + f"\n\n{instruction}"

    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
    for user_text, assistant_text in recent_turns:
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": assistant_text})
    messages.append({"role": "user", "content": user_message})

    return messages
