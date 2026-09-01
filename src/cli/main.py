import sys
import typing

from src.chat.conversation_engine import ConversationEngine
from src.config import get_env, load_config
from src.llm.fastembed_provider import FastEmbedProvider
from src.llm.groq_provider import GroqProvider
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA

EXIT_COMMANDS = {"/exit", "/quit", "exit", "quit"}


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

    print(f"{DEFAULT_PERSONA.name} is here. Type /exit to quit.", file=output_stream)

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

        response = engine.handle_message(user_message)
        print(response, file=output_stream)


if __name__ == "__main__":
    run()
