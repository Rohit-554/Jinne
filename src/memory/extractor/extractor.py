from src.llm.provider import LLMProvider
from src.memory.extractor.json_utils import parse_json_object
from src.memory.extractor.prompts import build_messages
from src.memory.extractor.schemas import ExtractionDecision, ExtractionResult, MemoryCandidate
from src.memory.models.memory import Memory
from src.memory.store.store import MemoryStore


class MemoryExtractor:
    def __init__(self, provider: LLMProvider):
        self._provider = provider

    def extract(self, message: str) -> list[MemoryCandidate]:
        raw_response = self._provider.complete(build_messages(message))
        parsed = parse_json_object(raw_response)
        result = ExtractionResult.model_validate(parsed)
        return result.candidates


def candidate_to_memory(candidate: MemoryCandidate, source_message_id: str) -> Memory:
    if candidate.decision != ExtractionDecision.SAVE:
        raise ValueError("Only SAVE candidates can be converted to a Memory")

    return Memory(
        type=candidate.type,
        subject=candidate.subject,
        relation=candidate.relation,
        value=candidate.value,
        importance=candidate.importance,
        confidence=candidate.confidence,
        source_message_id=source_message_id,
    )


def extract_and_store(
    extractor: MemoryExtractor,
    store: MemoryStore,
    message: str,
    source_message_id: str,
) -> list[Memory]:
    candidates = extractor.extract(message)
    saved: list[Memory] = []
    for candidate in candidates:
        if candidate.decision != ExtractionDecision.SAVE:
            continue
        memory = candidate_to_memory(candidate, source_message_id)
        saved.append(store.save(memory))
    return saved
