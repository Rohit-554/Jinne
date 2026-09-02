import groq
import pytest

from src.config import get_env, load_config
from src.llm.groq_provider import GroqProvider

load_config()

GROQ_API_KEY = get_env("GROQ_API_KEY")
GROQ_MODEL = get_env("GROQ_MODEL", default="openai/gpt-oss-120b")


@pytest.mark.skipif(not GROQ_API_KEY, reason="GROQ_API_KEY not set - skipping live smoke test")
def test_complete_returns_non_empty_response():
    provider = GroqProvider(api_key=GROQ_API_KEY, model=GROQ_MODEL)

    try:
        response = provider.complete(
            [{"role": "user", "content": "Reply with the single word: pong"}]
        )
    except groq.RateLimitError as exc:
        pytest.skip(f"Groq rate/quota limit hit, not a code issue: {exc}")

    assert isinstance(response, str)
    assert len(response.strip()) > 0


@pytest.mark.skipif(not GROQ_API_KEY, reason="GROQ_API_KEY not set - skipping live smoke test")
def test_complete_stream_yields_multiple_chunks_that_concatenate():
    provider = GroqProvider(api_key=GROQ_API_KEY, model=GROQ_MODEL)

    try:
        chunks = list(
            provider.complete_stream(
                [{"role": "user", "content": "Count from one to ten, one number per line."}]
            )
        )
    except groq.RateLimitError as exc:
        pytest.skip(f"Groq rate/quota limit hit, not a code issue: {exc}")

    assert len(chunks) > 1
    full_response = "".join(chunks)
    assert len(full_response.strip()) > 0
