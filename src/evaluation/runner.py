from typing import Callable, Protocol

from src.chat.conversation_engine import ConversationEngine
from src.evaluation.scenarios import Scenario
from src.llm.provider import EmbeddingProvider, LLMProvider
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA


class ConversationSystem(Protocol):
    def handle_message(self, user_message: str) -> str: ...


EngineFactory = Callable[[LLMProvider, EmbeddingProvider, MemoryStore], ConversationSystem]


def proposed_system_factory(llm: LLMProvider, embedder: EmbeddingProvider, store: MemoryStore) -> ConversationSystem:
    return ConversationEngine(llm=llm, embedder=embedder, store=store, persona=DEFAULT_PERSONA)


def run_scenario(
    scenario: Scenario,
    llm: LLMProvider,
    embedder: EmbeddingProvider,
    engine_factory: EngineFactory = proposed_system_factory,
) -> tuple[str, MemoryStore]:
    store = MemoryStore(":memory:")
    engine = engine_factory(llm, embedder, store)

    for turn in scenario.turns:
        engine.handle_message(turn)

    response = engine.handle_message(scenario.final_question)
    return response, store
