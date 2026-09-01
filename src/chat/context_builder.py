from src.memory.models.memory import Memory
from src.persona.persona import Persona
from src.persona.render import render_persona


def build_messages(
    persona: Persona,
    memories: list[Memory],
    recent_turns: list[tuple[str, str]],
    user_message: str,
) -> list[dict[str, str]]:
    persona_block = render_persona(persona)

    if memories:
        memory_lines = "\n".join(f"- {m.value}" for m in memories)
    else:
        memory_lines = "(none)"
    memory_block = f"RELEVANT USER MEMORY\n{memory_lines}"

    system_content = (
        f"{persona_block}\n\n{memory_block}\n\n"
        "Respond to the user in character. Weave in relevant memory only "
        "when it naturally fits; do not recite it as a list."
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
    for user_text, assistant_text in recent_turns:
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": assistant_text})
    messages.append({"role": "user", "content": user_message})

    return messages
