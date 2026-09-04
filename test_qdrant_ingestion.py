import asyncio
import uuid

from qdrant_client.models import PointStruct

from app.ollama.client import build_async_client
from app.ollama.service import OllamaService
from app.qdrant.client import build_async_client as build_qdrant_client
from app.qdrant.service import QdrantService


COLLECTION = "marketing_knowledge"


async def main():
    ollama_client = build_async_client()
    qdrant_client = build_qdrant_client()

    ollama_service = OllamaService(ollama_client)
    qdrant_service = QdrantService(qdrant_client)

    try:
        document = """
        AI Marketing Agent helps small businesses create effective
        marketing campaigns using artificial intelligence.

        The platform can generate social media content, campaign ideas,
        marketing strategies, SEO content, and lead generation campaigns.

        For LinkedIn marketing, businesses should focus on useful,
        educational content that demonstrates expertise and encourages
        engagement from their target audience.
        """

        print("Generating embedding...")

        vector = await ollama_service.embed(document)

        print("Embedding dimension:", len(vector))

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "document_id": "test-marketing-001",
                "source_type": "test",
                "knowledge_type": "marketing",
                "user_id": "system",
                "content": document,
            },
        )

        print("Inserting point into Qdrant...")

        await qdrant_service.insert_points(
            COLLECTION,
            [point],
        )

        print("Point inserted successfully.")

        info = await qdrant_service.get_collection_info(
            COLLECTION
        )

        print("Collection points:", info.points_count)

    finally:
        await ollama_client.aclose()
        await qdrant_client.close()


if __name__ == "__main__":
    asyncio.run(main())