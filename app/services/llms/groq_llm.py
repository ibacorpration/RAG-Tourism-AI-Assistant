import os
import re
from typing import Generator
from groq import Groq
from app.services.llms.base import BaseLLMProvider
from app.core.config import settings
from app.core.exceptions import RAGException, LLMRateLimitError
from app.core.logger import logger


class GroqAPIKeyError(RAGException):
    """Raised when GROQ_API_KEY is missing or invalid."""
    pass


def _friendly_rate_limit_message(raw_error: str) -> str:
    """
    Groq's 429 body is a raw JSON blob meant for developers, not end users.
    Extract the retry wait time if present and turn it into something a
    chat user can actually read, in both languages.
    """
    match = re.search(r"try again in ([0-9.]+)(m?s|m|h)", raw_error)
    wait_hint = ""
    if match:
        wait_hint = f" (~{match.group(1)}{match.group(2)})"
    return (
        f"وصلنا للحد اليومي المسموح به من الـ AI provider (Groq) مؤقتًا{wait_hint}. "
        "جرب تاني بعد شوية.\n"
        f"Daily rate limit reached on the AI provider (Groq) for now{wait_hint}. Please try again shortly."
    )


class GroqLLMProvider(BaseLLMProvider):
    """
    Dedicated Groq API LLM Provider for high-speed Llama-3 / Mixtral inference.
    """

    def __init__(self, api_key: str = None, model: str = None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = getattr(settings, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
        self.model = model or getattr(settings, "GROQ_MODEL_NAME", "llama-3.1-8b-instant")
        
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def _ensure_client(self):
        if not self.api_key or not self.client:
            raise GroqAPIKeyError(
                "GROQ_API_KEY is not set. Please add your Groq API key (GROQ_API_KEY=gsk_...) to your .env file."
            )

    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        self._ensure_client()
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            logger.info(f"Sending prompt to Groq API (model: {self.model})...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.2),
                max_tokens=kwargs.get("max_tokens", settings.LLM_MAX_TOKENS)
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "rate_limit_exceeded" in error_str or "429" in error_str:
                logger.error(f"Groq rate limit hit: {error_str}")
                raise LLMRateLimitError(_friendly_rate_limit_message(error_str))
            logger.error(f"Groq API call failed: {error_str}")
            raise RAGException(f"Groq API error: {error_str}")

    def generate_stream(self, prompt: str, system_prompt: str = None, **kwargs) -> Generator[str, None, None]:
        self._ensure_client()
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            logger.info(f"Starting Groq API stream (model: {self.model})...")
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.2),
                max_tokens=kwargs.get("max_tokens", settings.LLM_MAX_TOKENS),
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            error_str = str(e)
            if "rate_limit_exceeded" in error_str or "429" in error_str:
                logger.error(f"Groq rate limit hit (stream): {error_str}")
                raise LLMRateLimitError(_friendly_rate_limit_message(error_str))
            logger.error(f"Groq streaming API call failed: {error_str}")
            raise RAGException(f"Groq API streaming error: {error_str}")
