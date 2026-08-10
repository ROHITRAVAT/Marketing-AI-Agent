"""Reusable Qdrant service layer.

All Qdrant access is concentrated here so that API routes stay thin and Qdrant
logic is never embedded in HTTP layers. The service is built on the async
client so it can be used directly from FastAPI async endpoints.
"""

import asyncio
import logging
from typing import Any, Sequence

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from app.core.config import QDRANT_TIMEOUT
from app.qdrant.client import get_async_client
from app.qdrant.collections import DISTANCE, QDRANT_COLLECTIONS, VECTOR_SIZE

logger = logging.getLogger(__name__)


class QdrantService:
    """High-level, reusable operations against Qdrant."""

    def __init__(
        self,
        client: AsyncQdrantClient,
        *,
        timeout: float | None = None,
    ) -> None:
        self.client = client
        self.timeout = timeout if timeout is not None else QDRANT_TIMEOUT

    async def check_connection(self) -> bool:
        """Return True when Qdrant is reachable; raise on failure/timeout."""
        return await asyncio.wait_for(
            self._ping(),
            timeout=self.timeout,
        )

    async def _ping(self) -> bool:
        await self.client.get_collections()
        return True

    async def collection_exists(self, name: str) -> bool:
        """Return whether a collection with ``name`` exists."""
        return await asyncio.wait_for(
            self.client.collection_exists(collection_name=name),
            timeout=self.timeout,
        )

    async def create_collection(
        self,
        name: str,
        *,
        vector_size: int | None = None,
        distance: Distance = DISTANCE,
    ) -> bool:
        """Create a collection with a configurable vector size and distance.

        ``vector_size`` defaults to ``QDRANT_VECTOR_SIZE`` (see
        ``app/qdrant/collections.py``) and MUST match the embedding model.
        """
        size = vector_size if vector_size is not None else VECTOR_SIZE
        return await asyncio.wait_for(
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=size, distance=distance),
            ),
            timeout=self.timeout,
        )

    async def delete_collection(self, name: str) -> bool:
        """Explicitly delete a collection (only used when really intended)."""
        return await asyncio.wait_for(
            self.client.delete_collection(collection_name=name),
            timeout=self.timeout,
        )

    async def insert_points(
        self,
        name: str,
        points: Sequence[PointStruct],
    ) -> Any:
        """Insert/upsert points into a collection (waits for completion)."""
        return await asyncio.wait_for(
            self.client.upsert(
                collection_name=name,
                points=points,
                wait=True,
            ),
            timeout=self.timeout,
        )

    async def delete_points(
        self,
        name: str,
        point_ids: Sequence[int | str],
    ) -> Any:
        """Delete points by id from a collection (waits for completion)."""
        return await asyncio.wait_for(
            self.client.delete(
                collection_name=name,
                points_selector=PointIdsList(points=list(point_ids)),
                wait=True,
            ),
            timeout=self.timeout,
        )

    async def search(
        self,
        name: str,
        query_vector: Sequence[float],
        *,
        limit: int = 10,
    ) -> list:
        """Search a collection by vector similarity (COSINE), best match first."""
        response = await asyncio.wait_for(
            self.client.query_points(
                collection_name=name,
                query=list(query_vector),
                limit=limit,
                with_payload=True,
                with_vectors=False,
            ),
            timeout=self.timeout,
        )
        return response.points

    async def get_collection_info(self, name: str) -> Any:
        """Return collection metadata (status, config, points count, ...)."""
        return await asyncio.wait_for(
            self.client.get_collection(collection_name=name),
            timeout=self.timeout,
        )

    async def ensure_collections(self) -> dict[str, list[str]]:
        """Idempotently create the configured collections.

        Checks existence first and only creates missing collections — existing
        collections are never recreated, dropped, or repopulated. Safe to call
        on every application startup.
        """
        created: list[str] = []
        existing: list[str] = []
        for name in QDRANT_COLLECTIONS:
            if await self.collection_exists(name):
                existing.append(name)
                continue
            await self.create_collection(name)
            created.append(name)
            logger.info("Created Qdrant collection: %s", name)
        return {"created": created, "existing": existing}


def get_qdrant_service() -> QdrantService:
    """Dependency that exposes the application-wide Qdrant service."""
    return QdrantService(get_async_client())


async def ensure_qdrant_collections() -> dict[str, list[str]]:
    """Idempotent Qdrant collection initialization for application startup."""
    return await QdrantService(get_async_client()).ensure_collections()