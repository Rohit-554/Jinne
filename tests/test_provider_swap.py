from src.llm.provider import EmbeddingProvider, LLMProvider


class FakeLLMProvider:
    def __init__(self, canned_response: str):
        self._canned_response = canned_response

    def complete(self, messages: list[dict[str, str]]) -> str:
        return self._canned_response


class FakeEmbeddingProvider:
    def __init__(self, vector: list[float]):
        self._vector = vector

    def embed(self, text: str) -> list[float]:
        return self._vector


def run_completion(provider: LLMProvider, prompt: str) -> str:
    return provider.complete([{"role": "user", "content": prompt}])


def run_embedding(provider: EmbeddingProvider, text: str) -> list[float]:
    return provider.embed(text)


def test_fake_providers_satisfy_the_protocols():
    assert isinstance(FakeLLMProvider("hi"), LLMProvider)
    assert isinstance(FakeEmbeddingProvider([0.1]), EmbeddingProvider)


def test_swapping_llm_provider_does_not_change_calling_code():
    provider_a = FakeLLMProvider("response A")
    provider_b = FakeLLMProvider("response B")

    assert run_completion(provider_a, "hello") == "response A"
    assert run_completion(provider_b, "hello") == "response B"


def test_swapping_embedding_provider_does_not_change_calling_code():
    provider_a = FakeEmbeddingProvider([0.1, 0.2])
    provider_b = FakeEmbeddingProvider([0.9, 0.8])

    assert run_embedding(provider_a, "hello") == [0.1, 0.2]
    assert run_embedding(provider_b, "hello") == [0.9, 0.8]
