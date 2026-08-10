"""Centralized Ollama HTTP client configuration.

The httpx client is created exclusively from application configuration
(``app.ollama.config.OLLAMA_SETTINGS``), which is populated from environment
variables loaded from ``.env``. The Ollama URL therefore never appears in
source code.
"""

import logging
from functools import lru_cache

import httpx

from app.ollama.config import OLLAMA_SETTINGS

logger = logging.getLogger(__name__)


def build_async_client() -> httpx.AsyncClient:
    """Create a new :class:`httpx.AsyncClient` for the configured Ollama server.

    Uses the async client because the FastAPI application is fully async — a
    blocking HTTP client inside an async endpoint would block the event loop.
    """
    return httpx.AsyncClient(
        base_url=OLLAMA_SETTINGS.url,
        timeout=OLLAMA_SETTINGS.timeout,
    )


@lru_cache(maxsize=1)
def get_async_client() -> httpx.AsyncClient:
    """Return the application-wide singleton Ollama HTTP client (cached).

    The cache stays valid for the process lifetime of the FastAPI app. Use
    :func:`build_async_client` directly when a short-lived client is required
    (e.g. from tests or scripts).
    """
    return build_async_client()


async def close_async_client() -> None:
    """Close the cached Ollama HTTP client and clear the cache.

    Intended to be called from the application shutdown lifecycle; also makes
    the next call to :func:`get_async_client` create a fresh client.
    """
    try:
        await get_async_client().aclose()
    except Exception as exc:  # pragma: no cover - defensive cleanup
        logger.warning("Error while closing Ollama HTTP client: %s", exc)
    finally:
        get_async_client.cache_clear()