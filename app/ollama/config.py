"""Centralized Ollama configuration.

Reads the Ollama connection settings from the project's existing configuration
system (``app.core.config``), which in turn is populated from environment
variables loaded from ``.env``. No URL, host, or credentials are hard-coded in
application code — everything comes from configuration.
"""

from dataclasses import dataclass

from app.core.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_PORT,
    OLLAMA_TIMEOUT,
    OLLAMA_URL,
)


@dataclass(frozen=True)
class OllamaSettings:
    """Immutable snapshot of the Ollama connection settings.

    ``model`` may be empty — OLLAMA_MODEL is intentionally empty until Qwen 3
    is installed in a separate task.
    """

    host: str = OLLAMA_HOST
    port: int = OLLAMA_PORT
    url: str = OLLAMA_URL
    model: str = OLLAMA_MODEL
    embedding_model: str = OLLAMA_EMBEDDING_MODEL
    timeout: float = OLLAMA_TIMEOUT


# Process-wide settings object consumed by the client and service layers.
OLLAMA_SETTINGS = OllamaSettings()