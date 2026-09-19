"""
Test environment configuration.
Centralizes test-specific settings to avoid scattered magic strings.
"""
import os

# Test mode flag
TESTING = True

# SQLite for fast unit tests (no external dependencies needed)
TEST_SQLITE_URL = "sqlite+aiosqlite:///:memory:"

# PostgreSQL for true integration tests (requires running PG instance)
TEST_PG_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/marketing_test"
)

# Qdrant test collection (separate from production)
TEST_QDRANT_COLLECTION = os.getenv("TEST_QDRANT_COLLECTION", "test_marketing_vectors")

# Whether PostgreSQL is available for integration tests
PG_AVAILABLE = os.getenv("TEST_PG_AVAILABLE", "false").lower() == "true"
