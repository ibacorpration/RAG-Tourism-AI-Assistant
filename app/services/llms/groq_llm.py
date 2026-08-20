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
    """Convert Groq 429 errors into a user-friendly message."""
    return (
        "وصلنا للحد المسموح به من مزود الـ AI (Groq) مؤقتًا. "
        "جرب تاني بعد شوية.\n"
        "Daily rate limit reached on the AI provider (Groq). "
        "Please try again shortly."
    )

class GroqLLMProvider(BaseLLMProvider):
    """
    Groq LLM provider for the Tourism AI Assistant.
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = (
            api_key
            if api_key is not None
            else getattr(settings, "GROQ_API_KEY", None)
            or os.getenv("GROQ_API_KEY")
        )

        self.model = model or getattr(
            settings,
            "GROQ_MODEL_NAME",
            "openai/gpt-oss-120b"
        )

        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def _ensure_client(self):
        if not self.api_key or not self.client:
            raise GroqAPIKeyError(
                "GROQ_API_KEY is not set."
            )

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> str:

        self._ensure_client()

        try:
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            logger.info(
                f"Sending prompt to Groq API "
                f"(model: {self.model})..."
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.5),
                max_tokens=kwargs.get(
                    "max_tokens",
                    settings.LLM_MAX_TOKENS
                ),
            )

            content = response.choices[0].message.content

            return content or ""

        except Exception as e:
            error_str = str(e)

            if "rate_limit_exceeded" in error_str or "429" in error_str:
                logger.error(
                    f"Groq rate limit hit: {error_str}"
                )
                raise LLMRateLimitError(
                    _friendly_rate_limit_message(error_str)
                )

            logger.error(
                f"Groq API call failed: {error_str}"
            )

            raise RAGException(
                f"Groq API error: {error_str}"
            )

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> Generator[str, None, None]:

        self._ensure_client()

        try:
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            logger.info(
                f"Starting Groq API stream "
                f"(model: {self.model})..."
            )

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.5),
                max_tokens=kwargs.get(
                    "max_tokens",
                    settings.LLM_MAX_TOKENS
                ),
                stream=True,
            )

            for chunk in stream:

                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:
                    yield content

        except Exception as e:
            error_str = str(e)

            if "rate_limit_exceeded" in error_str or "429" in error_str:
                logger.error(
                    f"Groq rate limit hit (stream): {error_str}"
                )
                raise LLMRateLimitError(
                    _friendly_rate_limit_message(error_str)
                )

            logger.error(
                f"Groq API streaming failed: {error_str}"
            )

            raise RAGException(
                f"Groq API streaming error: {error_str}"
            )
