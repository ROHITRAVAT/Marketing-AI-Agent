"""Standalone infrastructure verification for Qdrant (FastAPI -> Qdrant).

Run inside the backend container so the connection uses the Docker network
(http://qdrant:6333), never localhost:

    docker compose exec backend python scripts/verify_qdrant.py

The script performs a full verify cycle and cleans up after itself:

    1. Qdrant is reachable
    2. a temporary test collection is created
    3. a test vector is inserted
    4. a vector search is performed
    5. the test point is removed
    6. the temporary collection is removed

Production collections are never touched; a temporary collection is used and
deleted regardless of success/failure.
"""

import asyncio
import math
import os
import sys

# Allow running as `python scripts/verify_qdrant.py` from any working directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

from app.core.config import (
    QDRANT_API_KEY,
    QDRANT_TIMEOUT,
    QDRANT_URL,
    QDRANT_VECTOR_SIZE,
)

COLLECTION = f"verify_temp_{uuid.uuid4().hex[:8]}"
POINT_ID = 424242


def _vector(seed: int = 7) -> list[float]:
    state = seed & 0x7FFFFFFF
    values = []
    for _ in range(QDRANT_VECTOR_SIZE):
        state = (state * 1103515245 + 12345) % (2**31)
        values.append((state % 1000) / 1000.0 - 0.5)
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


def _ok() -> None:
    print("      OK")


async def main() -> int:
    client = AsyncQdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY or None,
        timeout=QDRANT_TIMEOUT,
    )
    try:
        print(f"[1/6] Qdrant reachable at {QDRANT_URL} ...")
        await client.get_collections()
        _ok()

        print(f"[2/6] Creating temporary collection '{COLLECTION}' "
              f"(dim={QDRANT_VECTOR_SIZE}, COSINE) ...")
        await client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=QDRANT_VECTOR_SIZE, distance=Distance.COSINE
            ),
        )
        _ok()

        vector = _vector()
        print("[3/6] Inserting test vector ...")
        await client.upsert(
            collection_name=COLLECTION,
            points=[PointStruct(id=POINT_ID, vector=vector, payload={"source": "verify"})],
            wait=True,
        )
        _ok()

        print("[4/6] Performing vector search ...")
        response = await client.query_points(
            collection_name=COLLECTION, query=vector, limit=5, with_payload=True
        )
        hits = response.points
        assert hits, "search returned no results"
        top = hits[0]
        assert top.id == POINT_ID, f"expected point {POINT_ID}, got {top.id}"
        assert top.score > 0.99, f"expected near-1.0 COSINE score, got {top.score}"
        print(f"      OK (top hit id={top.id}, score={top.score:.4f})")

        print("[5/6] Deleting test point ...")
        await client.delete(
            collection_name=COLLECTION,
            points_selector=PointIdsList(points=[POINT_ID]),
            wait=True,
        )
        remaining = await client.retrieve(collection_name=COLLECTION, ids=[POINT_ID])
        assert remaining == [], "point still present after deletion"
        _ok()

        print("[6/6] Deleting temporary collection ...")
        await client.delete_collection(collection_name=COLLECTION)
        _ok()

        print("\nSUCCESS — Qdrant verified over the FastAPI/Docker network "
              f"({QDRANT_URL}). All temporary data cleaned up.\n")
        return 0
    except Exception as exc:  # noqa: BLE001 - report any failure clearly
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        try:
            if await client.collection_exists(COLLECTION):
                await client.delete_collection(COLLECTION, timeout=30)
        except Exception:
            pass
        await client.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))