import pytest
from app.services.llms.groq_llm import GroqLLMProvider, GroqAPIKeyError


def test_groq_provider_missing_key():
    provider = GroqLLMProvider(api_key="")
    with pytest.raises(GroqAPIKeyError):
        provider.generate(prompt="What is RAG?")
