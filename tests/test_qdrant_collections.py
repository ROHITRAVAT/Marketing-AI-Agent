import pytest
from unittest.mock import AsyncMock, patch, call
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

from app.qdrant.collections import COLLECTION_MARKETING_DOCUMENTS, DISTANCE, VECTOR_SIZE, QDRANT_COLLECTIONS
from app.qdrant.service import QdrantService


@pytest.fixture
def mock_qdrant_client():
    client = AsyncMock()
    # By default, assume no collections exist
    client.collection_exists.return_value = False
    return client


@pytest.fixture
def qdrant_service(mock_qdrant_client):
    return QdrantService(client=mock_qdrant_client, timeout=5.0)


@pytest.mark.asyncio
async def test_ensure_collections_creates_missing(qdrant_service, mock_qdrant_client):
    # Setup
    mock_qdrant_client.collection_exists.return_value = False

    # Execute
    result = await qdrant_service.ensure_collections()

    # Verify
    assert COLLECTION_MARKETING_DOCUMENTS in result["created"]
    assert COLLECTION_MARKETING_DOCUMENTS not in result["existing"]
    
    # Check that create_collection was called correctly
    mock_qdrant_client.create_collection.assert_called_once_with(
        collection_name=COLLECTION_MARKETING_DOCUMENTS,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE)
    )

    # Check payload indices
    expected_calls = [
        call(collection_name=COLLECTION_MARKETING_DOCUMENTS, field_name="document_id", field_schema=PayloadSchemaType.KEYWORD),
        call(collection_name=COLLECTION_MARKETING_DOCUMENTS, field_name="source_type", field_schema=PayloadSchemaType.KEYWORD),
        call(collection_name=COLLECTION_MARKETING_DOCUMENTS, field_name="knowledge_type", field_schema=PayloadSchemaType.KEYWORD),
        call(collection_name=COLLECTION_MARKETING_DOCUMENTS, field_name="user_id", field_schema=PayloadSchemaType.KEYWORD),
    ]
    mock_qdrant_client.create_payload_index.assert_has_calls(expected_calls, any_order=True)


@pytest.mark.asyncio
async def test_ensure_collections_idempotent(qdrant_service, mock_qdrant_client):
    # Setup: collection already exists
    mock_qdrant_client.collection_exists.return_value = True

    # Execute
    result = await qdrant_service.ensure_collections()

    # Verify
    assert COLLECTION_MARKETING_DOCUMENTS in result["existing"]
    assert COLLECTION_MARKETING_DOCUMENTS not in result["created"]
    
    # Should not attempt to recreate
    mock_qdrant_client.create_collection.assert_not_called()
    mock_qdrant_client.create_payload_index.assert_not_called()

def test_qdrant_collections_config():
    # Verify the vector config variables are set to their expected values
    assert COLLECTION_MARKETING_DOCUMENTS == "marketing_knowledge"
    assert QDRANT_COLLECTIONS == [COLLECTION_MARKETING_DOCUMENTS]
    assert DISTANCE == Distance.COSINE
