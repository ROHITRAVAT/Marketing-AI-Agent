import asyncio

from app.ollama.client import build_async_client
from app.ollama.service import OllamaService


async def main():
    client = build_async_client()

    try:
        service = OllamaService(client)

        vector = await service.embed(
            "AI marketing for small businesses"
        )

        print("Embedding dimension:", len(vector))
        print("First 5 values:", vector[:5])

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
