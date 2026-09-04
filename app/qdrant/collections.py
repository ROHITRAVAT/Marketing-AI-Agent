"""Qdrant collections used by the Marketing AI Agent.

VECTOR_SIZE is configurable via the ``QDRANT_VECTOR_SIZE`` environment variable.
The vector dimension MUST match the embedding model used to generate vectors.
"""

from qdrant_client.models import Distance

from app.core.config import QDRANT_VECTOR_SIZE


# Main collection used for marketing knowledge retrieval.
COLLECTION_MARKETING_DOCUMENTS = "marketing_knowledge"


QDRANT_COLLECTIONS = [
    COLLECTION_MARKETING_DOCUMENTS,
]


# Vector distance metric used for semantic search.
DISTANCE = Distance.COSINE


# Must match the embedding model dimension.
VECTOR_SIZE = QDRANT_VECTOR_SIZE