import pytest

from src.config import get_env, load_config
from src.llm.groq_provider import GroqProvider

load_config()

GROQ_API_KEY = get_env("GROQ_API_KEY")
GROQ_MODEL = get_env("GROQ_MODEL", default="openai/gpt-oss-120b")


@pytest.mark.skipif(not GROQ_API_KEY, reason="GROQ_API_KEY not set - skipping live smoke test")
def test_complete_returns_non_empty_response():
    provider = GroqProvider(api_key=GROQ_API_KEY, model=GROQ_MODEL)

    response = provider.complete(
        [{"role": "user", "content": "Reply with the single word: pong"}]
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0
