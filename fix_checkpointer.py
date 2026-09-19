import os

def fix_checkpointer_mock():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Add a mock for get_checkpointer in autouse fixture
    mock_str = """
@pytest.fixture(autouse=True)
def mock_worker_session(test_engine):
    from unittest.mock import patch
    
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    from langgraph.checkpoint.memory import MemorySaver
    from contextlib import asynccontextmanager
    
    # Create a single memory saver for the entire test
    test_checkpointer = MemorySaver()
    
    @asynccontextmanager
    async def mock_get_checkpointer():
        yield test_checkpointer
    
    with patch("app.scheduler.worker.AsyncSessionLocal", new=async_session), \\
         patch("app.agents.checkpoint.get_checkpointer", new=mock_get_checkpointer), \\
         patch("app.services.agent_service.get_checkpointer", new=mock_get_checkpointer):
        yield
"""
    import re
    content = re.sub(
        r'@pytest\.fixture\(autouse=True\)\ndef mock_worker_session\(test_engine\):.*?yield\s*',
        mock_str.strip(),
        content,
        flags=re.DOTALL
    )

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_checkpointer_mock()
