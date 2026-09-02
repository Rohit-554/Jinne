from pathlib import Path

import src.llm.provider as provider_module
from src.llm.provider import EmbeddingProvider, LLMProvider, StreamingLLMProvider

VENDOR_NAMES = ("groq", "fastembed", "openai", "anthropic", "google")


def test_llm_provider_is_a_protocol():
    assert LLMProvider._is_protocol is True


def test_streaming_llm_provider_is_a_protocol():
    assert StreamingLLMProvider._is_protocol is True


def test_embedding_provider_is_a_protocol():
    assert EmbeddingProvider._is_protocol is True


def test_provider_module_has_no_vendor_specific_imports():
    source = Path(provider_module.__file__).read_text().lower()
    for vendor in VENDOR_NAMES:
        assert vendor not in source, f"provider.py should not reference {vendor}"
