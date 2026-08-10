"""Reusable Ollama service layer.

All Ollama access is concentrated here so that API routes stay thin and Ollama
logic is never embedded in HTTP layers. The service uses httpx's async client
so it can be used directly from FastAPI async endpoints without blocking the
event loop.

The public API intentionally exposes no Ollama management endpoints — model
management stays internal. This service is consumed by the /health endpoint
(check_connection) and by internal scripts/tests (list_models).
"""

import asyncio
import logging
from typing import Any

import httpx

from app.ollama.client import get_async_client
from app.ollama.config import OLLAMA_SETTINGS

logger = logging.getLogger(__name__)


class OllamaService:
    """High-level, reusable operations against the Ollama server."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        timeout: float | None = None,
    ) -> None:
        self.client = client
        self.timeout = timeout if timeout is not None else OLLAMA_SETTINGS.timeout

    async def check_connection(self) -> bool:
        """Return True when Ollama is reachable; raise on failure/timeout."""
        await self._get_json("/api/tags")
        return True

    async def list_models(self) -> list[dict[str, Any]]:
        """Return the list of installed models.

        May legitimately be empty — no model is downloaded in this
        infrastructure task (Qwen 3 is installed in a separate task).
        """
        data = await self._get_json("/api/tags")
        return data.get("models", [])

    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        **options: Any,
    ) -> str:
        """Minimal single-turn completion wrapper (no agents/pipelines yet).

        Not wired to any public endpoint — provided as a ready building block
        for later tasks. Raises :class:`ValueError` when no model is configured
        (``OLLAMA_MODEL`` is intentionally empty until Qwen 3 is installed).
        """
        model_name = model or OLLAMA_SETTINGS.model
        if not model_name:
            raise ValueError(
                "No Ollama model configured. Set OLLAMA_MODEL once a model "
                "(e.g. Qwen 3) is installed."
            )
        payload = {"model": model_name, "prompt": prompt, "stream": False, **options}
        response = await asyncio.wait_for(
            self.client.post("/api/generate", json=payload),
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    async def _get_json(self, path: str) -> dict[str, Any]:
        response = await asyncio.wait_for(
            self.client.get(path),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()


def get_ollama_service() -> OllamaService:
    """Dependency that exposes the application-wide Ollama service."""
    return OllamaService(get_async_client())