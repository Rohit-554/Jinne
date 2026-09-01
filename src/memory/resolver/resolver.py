from src.llm.provider import LLMProvider
from src.memory.extractor.json_utils import parse_json_object
from src.memory.models.memory import Memory, MemoryStatus, utcnow
from src.memory.resolver.prompts import build_messages
from src.memory.resolver.schemas import ResolverAction, ResolverDecision
from src.memory.store.store import MemoryStore

CERTAINTY_THRESHOLD = 0.6


class MemoryResolver:
    def __init__(self, provider: LLMProvider):
        self._provider = provider

    def classify(
        self,
        candidate_memory: Memory,
        existing_related_memories: list[Memory],
    ) -> ResolverDecision:
        raw_response = self._provider.complete(build_messages(candidate_memory, existing_related_memories))
        parsed = parse_json_object(raw_response)
        return ResolverDecision.model_validate(parsed)

    def resolve(self, candidate_memory: Memory, store: MemoryStore) -> Memory | None:
        if candidate_memory.confidence < CERTAINTY_THRESHOLD:
            return candidate_memory.model_copy(update={"status": MemoryStatus.UNCERTAIN})

        existing_related = [
            memory
            for memory in store.list(status=MemoryStatus.ACTIVE)
            if memory.subject == candidate_memory.subject and memory.relation == candidate_memory.relation
        ]

        if not existing_related:
            return candidate_memory

        decision = self.classify(candidate_memory, existing_related)

        if decision.action == ResolverAction.DUPLICATE:
            return None

        if decision.action == ResolverAction.SUPERSEDE:
            store.update_status(decision.superseded_memory_id, MemoryStatus.SUPERSEDED, valid_until=utcnow())
            return candidate_memory.model_copy(update={"supersedes_memory_id": decision.superseded_memory_id})

        return candidate_memory
