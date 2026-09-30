import os
import pytest
import importlib
from unittest.mock import patch, mock_open

import app.core.config

@pytest.fixture
def mock_no_docker():
    original_exists = os.path.exists
    def side_effect(path):
        if path == "/.dockerenv":
            return False
        return original_exists(path)
    with patch("os.path.exists", side_effect=side_effect) as mock_exists:
        yield mock_exists

@pytest.fixture
def mock_docker():
    original_exists = os.path.exists
    def side_effect(path):
        if path == "/.dockerenv":
            return True
        return original_exists(path)
    with patch("os.path.exists", side_effect=side_effect) as mock_exists:
        yield mock_exists

def test_valid_ollama_model(mock_no_docker):
    with patch.dict(os.environ, {"OLLAMA_MODEL": "qwen3"}):
        importlib.reload(app.core.config)
        assert app.core.config.OLLAMA_MODEL == "qwen3"

def test_empty_ollama_model(mock_no_docker):
    with patch.dict(os.environ, {"OLLAMA_MODEL": ""}):
        with pytest.raises(ValueError, match="OLLAMA_MODEL must be set"):
            importlib.reload(app.core.config)

def test_whitespace_ollama_model(mock_no_docker):
    with patch.dict(os.environ, {"OLLAMA_MODEL": "   "}):
        with pytest.raises(ValueError, match="OLLAMA_MODEL must be set"):
            importlib.reload(app.core.config)

def test_valid_docker_database_url(mock_docker):
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://postgres:password@postgres:5432/mydb"}):
        importlib.reload(app.core.config)

def test_docker_localhost_database_url(mock_docker):
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/mydb"}):
        with pytest.raises(ValueError, match="DATABASE_URL points to localhost while the application is running inside a container"):
            importlib.reload(app.core.config)

def test_docker_127_0_0_1_database_url(mock_docker):
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://postgres:password@127.0.0.1:5432/mydb"}):
        with pytest.raises(ValueError, match="DATABASE_URL points to localhost while the application is running inside a container"):
            importlib.reload(app.core.config)

def test_docker_ipv6_localhost_database_url(mock_docker):
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://postgres:password@[::1]:5432/mydb"}):
        with pytest.raises(ValueError, match="DATABASE_URL points to localhost while the application is running inside a container"):
            importlib.reload(app.core.config)

def test_host_machine_localhost_database_url(mock_no_docker):
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/mydb"}):
        importlib.reload(app.core.config)

