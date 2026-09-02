import sys
import uuid

from src.chat.context_builder import build_messages
from src.llm.provider import EmbeddingProvider, LLMProvider
from src.memory.extractor.extractor import MemoryExtractor, extract_and_store
from src.memory.retriever.retriever import MemoryRetriever
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA
from src.persona.render import render_persona

RECENT_TURNS_WINDOW = 6


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


class BaselineBEngine:
    """Baseline B: naive vector memory. Reuses the proposed system's own
    extractor and retriever, but never resolves candidates against
    existing memories - every SAVE candidate becomes a new ACTIVE row
    forever, so a superseded fact stays exactly as retrievable as its
    replacement."""

    def __init__(self, llm: LLMProvider, embedder: EmbeddingProvider, store: MemoryStore):
        self._llm = llm
        self._embedder = embedder
        self._store = store
        self._persona = DEFAULT_PERSONA
        self._retriever = MemoryRetriever(embedder, store)
        self._extractor = MemoryExtractor(llm)
        self._recent_turns: list[tuple[str, str]] = []

    def handle_message(self, user_message: str) -> str:
        memories = self._retriever.retrieve(user_message)
        messages = build_messages(self._persona, memories, self._recent_turns, user_message)
        response = self._llm.complete(messages)

        self._recent_turns.append((user_message, response))
        self._recent_turns = self._recent_turns[-RECENT_TURNS_WINDOW:]

        message_id = str(uuid.uuid4())
        try:
            extract_and_store(
                self._extractor,
                self._store,
                user_message,
                message_id,
                embedder=self._embedder,
            )
        except Exception as exc:
            print(f"[memory update failed, continuing conversation: {exc!r}]", file=sys.stderr)

        return response


def baseline_b_factory(llm: LLMProvider, embedder: EmbeddingProvider, store: MemoryStore) -> BaselineBEngine:
    return BaselineBEngine(llm, embedder, store)
