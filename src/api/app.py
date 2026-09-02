import json
from collections.abc import Iterator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.api.serialization import memory_summary
from src.chat.conversation_engine import ConversationEngine
from src.config import get_env, load_config
from src.llm.fastembed_provider import FastEmbedProvider
from src.llm.groq_provider import GroqProvider
from src.memory.models.memory import MemoryStatus
from src.memory.store.store import MemoryStore
from src.persona.persona import DEFAULT_PERSONA

DEV_FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

app = FastAPI(title="Companion AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=DEV_FRONTEND_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

_engine: ConversationEngine | None = None


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


def get_engine() -> ConversationEngine:
    global _engine
    if _engine is None:
        _engine = build_engine()
    return _engine


class ChatRequest(BaseModel):
    message: str


def stream_chat_response(engine: ConversationEngine, message: str) -> Iterator[str]:
    try:
        for chunk in engine.handle_message_stream(message):
            yield f"event: chunk\ndata: {json.dumps({'text': chunk})}\n\n"
    except Exception as exc:
        yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"
        return

    scored = engine.get_last_retrieval_debug()
    created, updated = engine.get_last_turn_memory_changes()
    metadata = {
        "retrieved_memories": [memory_summary(s.memory) for s in scored],
        "created_memories": [memory_summary(m) for m in created],
        "updated_memories": [memory_summary(m) for m in updated],
    }
    yield f"event: done\ndata: {json.dumps(metadata)}\n\n"


@app.post("/api/chat")
def chat(request: ChatRequest, engine: ConversationEngine = Depends(get_engine)) -> StreamingResponse:
    return StreamingResponse(
        stream_chat_response(engine, request.message),
        media_type="text/event-stream",
    )


@app.get("/api/memories")
def list_memories(engine: ConversationEngine = Depends(get_engine)) -> dict:
    active = [m for m in engine.list_all_memories() if m.status == MemoryStatus.ACTIVE]
    return {"memories": [memory_summary(m) for m in active]}
