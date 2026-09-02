"""Qdrant collections used by the Marketing AI Agent.

VECTOR_SIZE is configurable via the ``QDRANT_VECTOR_SIZE`` environment variable
(default: 384 for infrastructure verification only).

WARNING: the vector dimension MUST match the embedding model used to generate
vectors in later phases (LangChain/embeddings). Changing the dimension after a
collection has been created requires recreating that collection.
"""

from qdrant_client.models import Distance

from app.core.config import QDRANT_VECTOR_SIZE

# Application collections (all created with COSINE distance).
COLLECTION_MARKETING_DOCUMENTS = "marketing_documents"

QDRANT_COLLECTIONS = [
    COLLECTION_MARKETING_DOCUMENTS,
]

# Vector distance metric used for all collections.
DISTANCE = Distance.COSINE

# Vector dimension for all collections — MUST match the embedding model (see
# the warning above and ``QDRANT_VECTOR_SIZE`` in ``app/core/config.py``).
VECTOR_SIZE = QDRANT_VECTOR_SIZE