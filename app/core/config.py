from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")
DEBUG = os.getenv("DEBUG")

# Comma-separated list of allowed CORS origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database — credentials must be provided via environment variables
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

# SQLAlchemy engine echo based on DEBUG
DB_ECHO = os.getenv("DB_ECHO", "True" if DEBUG == "True" else "False").lower() == "true"

# Qdrant vector database — Docker service name used as host inside the Docker network.
# Credentials must be provided via environment variables, never hard-coded here.
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_GRPC_PORT = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
QDRANT_URL = os.getenv("QDRANT_URL", f"http://{QDRANT_HOST}:{QDRANT_PORT}")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# Vector dimension used when creating Qdrant collections.
# WARNING: this MUST match the dimensionality of the embedding model that will
# generate vectors in later phases. Changing it after creating a collection
# requires recreating that collection.
QDRANT_VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", "384"))

# Timeout (seconds) for Qdrant client operations (health checks, upserts, searches).
QDRANT_TIMEOUT = float(os.getenv("QDRANT_TIMEOUT", "10"))

# Ollama LLM server — Docker service name used as host inside the Docker network.
# URL and model are provided via environment variables, never hard-coded here.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
OLLAMA_URL = os.getenv("OLLAMA_URL", f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")

# Model to use for inference. Kept EMPTY on purpose: the model (Qwen 3) is
# installed in a separate task. Infrastructure connectivity must already work
# without any model downloaded.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")

# Timeout (seconds) for Ollama HTTP operations (health checks, model listing).
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "30"))