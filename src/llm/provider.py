from collections.abc import Iterator
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


@runtime_checkable
class StreamingLLMProvider(Protocol):
    def complete_stream(self, messages: list[dict[str, str]]) -> Iterator[str]: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...
