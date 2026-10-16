from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

APP_NAME = os.getenv("APP_NAME") or "Marketing AI Agent"
APP_VERSION = os.getenv("APP_VERSION") or "1.0.0"
DEBUG = os.getenv("DEBUG")

# JWT authentication configuration
# Secret key must be provided through environment variables.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# JWT signing algorithm
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# OAuth token encryption key (Fernet requires 32 url-safe base64-encoded bytes)
# If not provided, it will dynamically generate a random one for dev, but tokens won't persist across restarts!
OAUTH_ENCRYPTION_KEY = os.getenv("OAUTH_ENCRYPTION_KEY")

# Access token lifetime in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
)

# Password reset token lifetime in minutes.
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30")
)

# Comma-separated list of allowed CORS origins.
# Vite commonly runs on 127.0.0.1 and localhost depending on the browser host,
# so allow both during local development.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

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
# For all-minilm, the vector size is 384.
QDRANT_VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", "384"))

# Timeout (seconds) for Qdrant client operations (health checks, upserts, searches).
QDRANT_TIMEOUT = float(os.getenv("QDRANT_TIMEOUT", "10"))

# Ollama LLM server — Docker service name used as host inside the Docker network.
# URL and model are provided via environment variables, never hard-coded here.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
OLLAMA_URL = os.getenv("OLLAMA_URL", f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")

# Default language model used for inference. Qwen 3 is the application default
# so generation works out of the box when the model is installed in Ollama.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3")

# Embedding model to use for generating vector embeddings.
# Example: "all-minilm" (384 dimensions)
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "all-minilm")

# Timeout (seconds) for Ollama HTTP operations (health checks, model listing).
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "30"))

# Concurrency limit for CPU-bound Ollama inference (default: 1)
OLLAMA_CONCURRENCY_LIMIT = int(os.getenv("OLLAMA_CONCURRENCY_LIMIT", "1"))

# Email / SMTP configuration
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL",
    "no-reply@example.com",
)
SMTP_FROM_NAME = os.getenv(
    "SMTP_FROM_NAME",
    "Marketing AI Agent",
)

# Frontend URL used when generating password-reset links.
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

# LangChain runtime defaults used by the Ollama-backed chat wrappers.
LANGCHAIN_TEMPERATURE = float(os.getenv("LANGCHAIN_TEMPERATURE", "0.2"))
LANGCHAIN_MAX_TOKENS = int(os.getenv("LANGCHAIN_MAX_TOKENS", "1024"))
LANGCHAIN_TOP_P = float(os.getenv("LANGCHAIN_TOP_P", "0.9"))
LANGCHAIN_TOP_K = int(os.getenv("LANGCHAIN_TOP_K", "40"))

# LinkedIn Configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/linkedin/callback")

# Facebook / Meta Configuration
META_APP_ID = os.getenv("META_APP_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
META_REDIRECT_URI = os.getenv("META_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/facebook/callback")

# Twitter / X Configuration
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID", "")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/twitter/callback")

# Scheduler Service Configuration
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
SCHEDULER_INTERVAL_SECONDS = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "60"))
SCHEDULER_MAX_RETRIES = int(os.getenv("SCHEDULER_MAX_RETRIES", "3"))

# Fail-Fast Configuration Validation
def validate_configuration():
    if not OLLAMA_MODEL or not OLLAMA_MODEL.strip():
        raise ValueError(
            "Configuration validation failed:\n"
            "OLLAMA_MODEL must be set to a non-empty value."
        )

    if OLLAMA_CONCURRENCY_LIMIT < 1:
        raise ValueError(
            "Configuration validation failed:\n"
            "OLLAMA_CONCURRENCY_LIMIT must be an integer >= 1."
        )

    is_docker = os.path.exists("/.dockerenv")
    if not is_docker:
        try:
            with open("/proc/1/cgroup", "rt") as f:
                if "docker" in f.read() or "kubepods" in f.read():
                    is_docker = True
        except Exception:
            pass

    if is_docker and DATABASE_URL:
        from urllib.parse import urlparse
        try:
            parsed = urlparse(DATABASE_URL)
            hostname = parsed.hostname
            if hostname in ("localhost", "127.0.0.1", "::1"):
                raise ValueError(
                    "Configuration validation failed:\n"
                    "DATABASE_URL points to localhost while the application is running inside a container.\n"
                    "Use the Docker Compose service name (for example, 'postgres') instead of localhost."
                )
        except ValueError as e:
            if "Configuration validation failed" in str(e):
                raise

validate_configuration()
