from src.chat.context_builder import build_messages
from src.memory.models.memory import Memory, MemoryType
from src.persona.persona import DEFAULT_PERSONA


def _make_memory(value: str) -> Memory:
    return Memory(
        type=MemoryType.EVENT,
        subject="user",
        relation="upcoming_event",
        value=value,
        importance=0.8,
        confidence=0.9,
        source_message_id="msg-seed",
    )


def test_build_messages_includes_persona_memories_history_and_current_message():
    memories = [_make_memory("Stripe interview tomorrow")]
    recent_turns = [("I'm training for a marathon", "That's exciting! How's training going?")]
    user_message = "I'm really nervous about tomorrow"

    messages = build_messages(DEFAULT_PERSONA, memories, recent_turns, user_message)

    system_content = messages[0]["content"]
    assert messages[0]["role"] == "system"
    assert DEFAULT_PERSONA.name in system_content
    assert "Stripe interview tomorrow" in system_content

    history_contents = [m["content"] for m in messages[1:-1]]
    assert "I'm training for a marathon" in history_contents
    assert "That's exciting! How's training going?" in history_contents

    assert messages[-1] == {"role": "user", "content": user_message}


def test_build_messages_with_no_memories_still_includes_all_other_sections():
    messages = build_messages(DEFAULT_PERSONA, [], [], "hello")

    assert DEFAULT_PERSONA.name in messages[0]["content"]
    assert "RELEVANT USER MEMORY" in messages[0]["content"]
    assert messages[-1] == {"role": "user", "content": "hello"}
