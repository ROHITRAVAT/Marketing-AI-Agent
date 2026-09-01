"""Centralized LangChain configuration.

The LangChain layer reuses the Ollama connection settings from
``app.ollama.config`` so model calls stay aligned with the rest of the
application. Additional generation defaults are read from the shared core
configuration module.
"""

from dataclasses import dataclass

from app.core.config import (
    LANGCHAIN_MAX_TOKENS,
    LANGCHAIN_TEMPERATURE,
    LANGCHAIN_TOP_K,
    LANGCHAIN_TOP_P,
)
from app.ollama.config import OLLAMA_SETTINGS


@dataclass(frozen=True)
class LangChainSettings:
    """Immutable snapshot of the LangChain runtime settings."""

    host: str = OLLAMA_SETTINGS.host
    port: int = OLLAMA_SETTINGS.port
    base_url: str = OLLAMA_SETTINGS.url
    model: str = OLLAMA_SETTINGS.model
    temperature: float = LANGCHAIN_TEMPERATURE
    max_tokens: int = LANGCHAIN_MAX_TOKENS
    top_p: float = LANGCHAIN_TOP_P
    top_k: int = LANGCHAIN_TOP_K


LANGCHAIN_SETTINGS = LangChainSettings()