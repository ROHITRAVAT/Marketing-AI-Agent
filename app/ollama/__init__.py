"""Ollama (local LLM server) integration.

This package centralizes everything related to Ollama so that API routes stay
thin and Ollama logic lives in one place:

- config.py  — centralized Ollama configuration (read from app.core.config)
- client.py  — centralized httpx async client creation from configuration
- service.py — reusable operations (check_connection, list_models, generate)
"""

from app.ollama.client import (
    build_async_client,
    close_async_client,
    get_async_client,
)
from app.ollama.service import (
    OllamaService,
    get_ollama_service,
)

__all__ = [
    "OllamaService",
    "build_async_client",
    "close_async_client",
    "get_async_client",
    "get_ollama_service",
]