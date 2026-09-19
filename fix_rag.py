import os
import re

def add_rag_mock():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    rag_mock = """
@pytest.fixture(autouse=True)
def mock_rag_services():
    from unittest.mock import patch, AsyncMock
    with patch("app.ollama.service.OllamaService.embed", new_callable=AsyncMock) as mock_embed, \\
         patch("app.qdrant.service.QdrantService.search", new_callable=AsyncMock) as mock_search:
        mock_embed.return_value = [0.1] * 768
        mock_search.return_value = []
        yield
"""
    
    # Insert it before integration_client
    content = content.replace("@pytest_asyncio.fixture\nasync def integration_client", rag_mock + "\n@pytest_asyncio.fixture\nasync def integration_client")

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    add_rag_mock()
