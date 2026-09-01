from src.llm.provider import EmbeddingProvider
from src.memory.models.memory import Memory


def build_embedding_text(memory: Memory) -> str:
    return f"{memory.relation.replace('_', ' ')} {memory.value}"


def embed_memory(embedder: EmbeddingProvider, memory: Memory) -> Memory:
    vector = embedder.embed(build_embedding_text(memory))
    return memory.model_copy(update={"embedding": vector})
