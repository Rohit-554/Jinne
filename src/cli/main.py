import sys
import typing

from src.chat.conversation_engine import ConversationEngine
from src.cli.memory_commands import render_memory_debug, render_memory_timeline
from src.config import get_env, load_config
from src.llm.fastembed_provider import FastEmbedProvider
from src.llm.groq_provider import GroqProvider
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA

EXIT_COMMANDS = {"/exit", "/quit", "exit", "quit"}
TIMELINE_COMMANDS = {"/memories", "/memory-timeline"}
DEBUG_COMMANDS = {"/memory-debug"}


def build_engine() -> ConversationEngine:
    load_config()
    groq_api_key = get_env("GROQ_API_KEY", required=True)
    groq_model = get_env("GROQ_MODEL", default="openai/gpt-oss-120b")
    embedding_model = get_env("EMBEDDING_MODEL", default="BAAI/bge-small-en-v1.5")
    db_path = get_env("MEMORY_DB_PATH", default="./companion.db")

    llm = GroqProvider(api_key=groq_api_key, model=groq_model)
    embedder = FastEmbedProvider(model_name=embedding_model)
    store = MemoryStore(db_path)

    return ConversationEngine(llm=llm, embedder=embedder, store=store, persona=DEFAULT_PERSONA)


def run(
    engine: ConversationEngine | None = None,
    input_stream: typing.TextIO = sys.stdin,
    output_stream: typing.TextIO = sys.stdout,
) -> None:
    if engine is None:
        engine = build_engine()

    print(
        f"{DEFAULT_PERSONA.name} is here. Type /exit to quit, /memories for the timeline, /memory-debug for the last retrieval.",
        file=output_stream,
    )

    while True:
        print("> ", end="", file=output_stream, flush=True)
        line = input_stream.readline()
        if not line:
            break

        user_message = line.strip()
        if not user_message:
            continue
        if user_message.lower() in EXIT_COMMANDS:
            break
        if user_message.lower() in TIMELINE_COMMANDS:
            print(render_memory_timeline(engine.list_all_memories()), file=output_stream)
            continue
        if user_message.lower() in DEBUG_COMMANDS:
            print(render_memory_debug(engine.get_last_retrieval_debug()), file=output_stream)
            continue

        try:
            response = engine.handle_message(user_message)
        except Exception as exc:
            print(f"(sorry, something went wrong on that turn: {exc!r})", file=output_stream)
            continue
        print(response, file=output_stream)


if __name__ == "__main__":
    run()
