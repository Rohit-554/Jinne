from src.llm.provider import EmbeddingProvider, LLMProvider
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA
from src.persona.render import render_persona


class BaselineAEngine:
    """Baseline A: conversation context only, no persistent memory at
    all. Each turn sends the persona and the full raw conversation
    history so far, with no extraction, retrieval, or storage."""

    def __init__(self, llm: LLMProvider):
        self._llm = llm
        self._persona = DEFAULT_PERSONA
        self._history: list[tuple[str, str]] = []

    def handle_message(self, user_message: str) -> str:
        persona_block = render_persona(self._persona)
        messages = [{"role": "system", "content": persona_block}]
        for user_text, assistant_text in self._history:
            messages.append({"role": "user", "content": user_text})
            messages.append({"role": "assistant", "content": assistant_text})
        messages.append({"role": "user", "content": user_message})

        response = self._llm.complete(messages)
        self._history.append((user_message, response))
        return response


def baseline_a_factory(llm: LLMProvider, embedder: EmbeddingProvider, store: MemoryStore) -> BaselineAEngine:
    return BaselineAEngine(llm)
