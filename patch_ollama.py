import os
import re

def patch_ollama_service():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_rag_mock = """
@pytest.fixture(autouse=True)
def mock_rag_services():
    from unittest.mock import patch, AsyncMock, MagicMock
    
    mock_ollama = MagicMock()
    mock_ollama.embed = AsyncMock(return_value=[0.1] * 768)
    
    mock_qdrant = MagicMock()
    mock_qdrant.search = AsyncMock(return_value=[])
    
    with patch("app.agents.nodes.retrieval.get_ollama_service", return_value=mock_ollama), \\
         patch("app.agents.nodes.retrieval.get_qdrant_service", return_value=mock_qdrant):
        yield
"""

    content = re.sub(
        r'@pytest\.fixture\(autouse=True\)\ndef mock_rag_services\(\):.*?yield\n',
        new_rag_mock,
        content,
        flags=re.DOTALL
    )

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    patch_ollama_service()
