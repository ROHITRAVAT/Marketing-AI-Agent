"""Centralized Qdrant client configuration.

The client is created exclusively from application configuration
(``app.core.config``), which in turn is populated from environment variables
loaded from ``.env``. Connection URL and credentials therefore never appear in
source code.
"""

import logging
from functools import lru_cache

from qdrant_client import AsyncQdrantClient

from app.core.config import QDRANT_API_KEY, QDRANT_TIMEOUT, QDRANT_URL

logger = logging.getLogger(__name__)


def build_async_client() -> AsyncQdrantClient:
    """Create a new :class:`AsyncQdrantClient` from application configuration.

    Uses the async client (HTTP) because the FastAPI application is fully
    async — a blocking Qdrant client inside an async endpoint would block the
    event loop. ``api_key`` is passed as ``None`` when empty so no
    ``api-key`` header is sent while authentication is disabled.
    """
    return AsyncQdrantClient(
        url=QDRANT_URL,
        api_key=(QDRANT_API_KEY or None),
        timeout=QDRANT_TIMEOUT,
    )


@lru_cache(maxsize=1)
def get_async_client() -> AsyncQdrantClient:
    """Return the application-wide singleton Qdrant client (cached).

    The cache stays valid for the process lifetime of the FastAPI app. Use
    :func:`build_async_client` directly when a short-lived client is required
    (e.g. from tests or scripts).
    """
    return build_async_client()


async def close_async_client() -> None:
    """Close the cached Qdrant client and clear the cache.

    Intended to be called from the application shutdown lifecycle; also makes
    the next call to :func:`get_async_client` create a fresh client.
    """
    try:
        await get_async_client().close()
    except Exception as exc:  # pragma: no cover - defensive cleanup
        logger.warning("Error while closing Qdrant client: %s", exc)
    finally:
        get_async_client.cache_clear()