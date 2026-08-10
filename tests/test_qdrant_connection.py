"""Qdrant connectivity and CRUD tests.

Requires the Qdrant container to be running and reachable.

Run inside the backend container (FastAPI -> Qdrant over the Docker network):
    docker compose exec backend pytest tests/test_qdrant_connection.py -v

Every test uses its own temporary collection (unique name) and cleans up after
itself, including explicit point/collection removal. No permanent data is ever
written to production collections.
"""

import math
import uuid

import pytest
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import (
    QDRANT_API_KEY,
    QDRANT_TIMEOUT,
    QDRANT_URL,
    QDRANT_VECTOR_SIZE,
)
from app.qdrant.collections import QDRANT_COLLECTIONS
from app.qdrant.service import QdrantService


def _test_collection_name() -> str:
    return f"pytest_marketing_{uuid.uuid4().hex[:12]}"


def _vector(seed: int = 0) -> list[float]:
    """Deterministic pseudo-random unit vector of QDRANT_VECTOR_SIZE dims."""
    state = seed & 0x7FFFFFFF
    values = []
    for _ in range(QDRANT_VECTOR_SIZE):
        state = (state * 1103515245 + 12345) % (2**31)
        values.append((state % 1000) / 1000.0 - 0.5)
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


@pytest.fixture
async def qdrant_client():
    """Async Qdrant client, fresh per test (own event loop); skips if unreachable."""
    client = AsyncQdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY or None,
        timeout=QDRANT_TIMEOUT,
    )
    try:
        await client.get_collections()
    except Exception as exc:  # pragma: no cover - env not started
        await client.close()
        pytest.skip(f"Qdrant unreachable at {QDRANT_URL}: {exc}")
    yield client
    await client.close()


@pytest.fixture
async def service(qdrant_client) -> QdrantService:
    """QdrantService bound to the per-test client."""
    return QdrantService(qdrant_client, timeout=QDRANT_TIMEOUT)


@pytest.fixture
async def test_collection(qdrant_client):
    """A disposable collection; always deleted after the test."""
    name = _test_collection_name()
    await qdrant_client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=QDRANT_VECTOR_SIZE, distance=Distance.COSINE),
    )
    yield name
    try:
        if await qdrant_client.collection_exists(name):
            await qdrant_client.delete_collection(name, timeout=30)
    except Exception:  # pragma: no cover - defensive cleanup
        pass


# ─── Tests ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_qdrant_connectivity(service):
    """Qdrant is reachable through the configured URL."""
    assert await service.check_connection() is True


@pytest.mark.asyncio
async def test_collection_creation_and_retrieval(service):
    """A collection can be created, detected, and inspected."""
    name = _test_collection_name()
    try:
        assert await service.create_collection(name) is True
        assert await service.collection_exists(name) is True

        info = await service.get_collection_info(name)
        vectors = info.config.params.vectors
        assert vectors.size == QDRANT_VECTOR_SIZE
        assert vectors.distance == Distance.COSINE
    finally:
        if await service.collection_exists(name):
            await service.delete_collection(name)


@pytest.mark.asyncio
async def test_vector_insertion(service, test_collection):
    """A vector point can be inserted and retrieved with its payload."""
    await service.insert_points(
        test_collection,
        [PointStruct(id=1, vector=_vector(1), payload={"source": "pytest"})],
    )
    records = await service.client.retrieve(
        collection_name=test_collection, ids=[1], with_payload=True
    )
    assert [r.id for r in records] == [1]
    assert records[0].payload.get("source") == "pytest"


@pytest.mark.asyncio
async def test_vector_search(service, test_collection):
    """Inserting a vector and searching for it returns it as the top hit."""
    query = _vector(99)
    await service.insert_points(
        test_collection,
        [PointStruct(id=1, vector=query, payload={"name": "needle"})],
    )
    await service.insert_points(
        test_collection,
        [PointStruct(id=i, vector=_vector(i), payload={"name": f"noise-{i}"}) for i in range(2, 6)],
    )

    hits = await service.search(test_collection, query, limit=3)
    assert hits, "search must return at least one hit"
    assert hits[0].id == 1, "exact-match vector should be the top hit"
    assert hits[0].score > 0.99, "COSINE similarity of identical unit vectors ~ 1.0"
    assert hits[0].payload.get("name") == "needle"


@pytest.mark.asyncio
async def test_point_and_collection_cleanup(service, test_collection):
    """A test point can be explicitly deleted; the temp collection is auto-removed."""
    point_id = str(uuid.uuid4())  # Qdrant accepts uint or canonical UUID ids
    await service.insert_points(
        test_collection, [PointStruct(id=point_id, vector=_vector(3))]
    )
    assert (
        await service.client.retrieve(
            collection_name=test_collection, ids=[point_id], with_payload=False
        )
    )

    await service.delete_points(test_collection, [point_id])
    assert (
        await service.client.retrieve(
            collection_name=test_collection, ids=[point_id], with_payload=False
        )
        == []
    ), "point should be gone after deletion"

    assert await service.collection_exists(test_collection) is True
    await service.delete_collection(test_collection)
    assert await service.collection_exists(test_collection) is False


@pytest.mark.asyncio
async def test_collection_initialization_is_idempotent(service):
    """ensure_collections() creates missing collections and is safe to rerun."""
    first = await service.ensure_collections()
    second = await service.ensure_collections()

    all_names = set(first["created"] + first["existing"])
    assert all_names == set(QDRANT_COLLECTIONS), "all app collections present after init"
    assert second["created"] == [], "second run must not recreate anything"
    assert set(second["existing"]) == set(QDRANT_COLLECTIONS)