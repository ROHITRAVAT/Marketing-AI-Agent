"""Qdrant vector database integration.

This package centralizes everything related to Qdrant so that API routes stay
thin and Qdrant logic lives in one place:

- client.py      — centralized AsyncQdrantClient creation from configuration
- collections.py — names and parameters of the application collections
- service.py     — reusable operations + idempotent initialization
"""

from app.qdrant.client import (
    build_async_client,
    close_async_client,
    get_async_client,
)
from app.qdrant.service import (
    QdrantService,
    ensure_qdrant_collections,
    get_qdrant_service,
)

__all__ = [
    "QdrantService",
    "build_async_client",
    "close_async_client",
    "ensure_qdrant_collections",
    "get_async_client",
    "get_qdrant_service",
]