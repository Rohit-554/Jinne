from src.chat.conversation_engine import ConversationEngine
from src.evaluation.scenarios import Scenario
from src.llm.provider import EmbeddingProvider, LLMProvider
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA


def run_scenario(
    scenario: Scenario,
    llm: LLMProvider,
    embedder: EmbeddingProvider,
) -> tuple[str, MemoryStore]:
    store = MemoryStore(":memory:")
    engine = ConversationEngine(llm=llm, embedder=embedder, store=store, persona=DEFAULT_PERSONA)

    for turn in scenario.turns:
        engine.handle_message(turn)

    response = engine.handle_message(scenario.final_question)
    return response, store
