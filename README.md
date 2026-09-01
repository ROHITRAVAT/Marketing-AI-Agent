# Marketing AI Agent

An AI-powered marketing assistant that helps businesses plan, create, and manage
marketing campaigns. Built with a FastAPI backend and a React + TypeScript frontend.

>**Work in progress** — the project scaffold is in place, but core AI features
> are not implemented yet.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI |
| Frontend | React · TypeScript · Vite |
| Database | PostgreSQL 16 · SQLAlchemy 2.x (async) · Alembic |
| Vector database | Qdrant · qdrant-client (async) |
| LLM runtime | Ollama (Docker) · httpx (async) |
| LLM orchestration | LangChain · LangGraph · prompt templates · output parsers |
| Browser automation | OpenClaw (cmdop) |
| Version control | Git |

---

## PostgreSQL Architecture

The database layer is built with **SQLAlchemy 2.x** using the **async** API and
**asyncpg** as the PostgreSQL driver. The architecture is modular:

```
app/database/
├── __init__.py      # Re-exports Base, engine, SessionLocal, get_db
├── connection.py    # Async SQLAlchemy engine (pooling, echo config)
├── session.py       # async_sessionmaker + get_db() dependency
└── base.py          # Declarative Base for future ORM models
```

- **Engine** (`connection.py`): Created with `create_async_engine`, configured
  with connection pooling (`pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`)
  and `echo` controlled by the `DB_ECHO` / `DEBUG` environment variable.
- **Session** (`session.py`): `async_sessionmaker` bound to the engine with
  `expire_on_commit=False`. The `get_db()` generator safely opens and closes
  sessions per request.
- **Base** (`base.py`): Declarative `Base` that all future ORM models inherit from.
- **Migrations** (`alembic/`): Alembic configured for async PostgreSQL. The
  database URL is read from `DATABASE_URL` at runtime — never hard-coded.

---

## Qdrant Architecture

The vector database layer is built on **Qdrant** and **qdrant-client** using
the **async** client, so it can be used directly from FastAPI async endpoints
without blocking the event loop. Qdrant runs as a Docker Compose service and
FastAPI talks to it over the Docker network — never through `localhost`.

```
app/qdrant/
├── __init__.py      # Re-exports client/service helpers
├── client.py        # Centralized AsyncQdrantClient creation (from config)
├── collections.py   # Collection names, distance metric, vector size
└── service.py       # QdrantService: connectivity, CRUD, idempotent init
```

- **Client** (`client.py`): builds an `AsyncQdrantClient` from `QDRANT_URL`,
  `QDRANT_API_KEY`, and `QDRANT_TIMEOUT`. A process-wide singleton is cached
  and closed on application shutdown.
- **Collections** (`collections.py`): declares the three application
  collections (all COSINE distance) and the configurable vector size.
- **Service** (`service.py`): reusable operations — connectivity check,
  collection existence / create / delete, insert / delete points, vector
  search, collection info, and an idempotent `ensure_collections()`.
- **Startup init** (`app/main.py`): `ensure_qdrant_collections()` runs on boot
  and creates **only missing** collections. Existing collections are never
  dropped or repopulated, so application restarts are safe.

### Collections

| Collection | Distance | Purpose (future phases) |
|---|---|---|
| `marketing_content` | COSINE | Generated marketing content |
| `marketing_knowledge` | COSINE | Brand/reference knowledge base |
| `marketing_campaigns` | COSINE | Campaign embeddings & metadata |

### Vector dimension configuration

The vector dimension is **not** hard-coded: it is read from
`QDRANT_VECTOR_SIZE` (default `384`). The default of 384 exists so the
infrastructure can be verified with a cheap dimensionality.

> ⚠️ **WARNING:** `QDRANT_VECTOR_SIZE` MUST match the dimensionality of the
> embedding model used to generate vectors in later phases. Qdrant does not
> support changing the dimension of an existing collection in place — if the
> value changes, existing collections must be recreated.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|---|---|---|
| `APP_NAME` | Application name | `Marketing AI Agent` |
| `APP_VERSION` | Application version | `1.0.0` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:5173` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `POSTGRES_HOST` | PostgreSQL host (Docker service name) | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | Database name | `marketing_ai` |
| `POSTGRES_USER` | Application database user | `marketing` |
| `POSTGRES_PASSWORD` | Application database password | *(secret)* |
| `DATABASE_URL` | Full async SQLAlchemy URL | `postgresql+asyncpg://user:pass@postgres:5432/db` |
| `QDRANT_HOST` | Qdrant host (Docker service name) | `qdrant` |
| `QDRANT_PORT` | Qdrant HTTP port | `6333` |
| `QDRANT_GRPC_PORT` | Qdrant gRPC port | `6334` |
| `QDRANT_URL` | Full Qdrant URL (Docker network) | `http://qdrant:6333` |
| `QDRANT_API_KEY` | Qdrant API key (empty = auth disabled) | *(empty)* |
| `QDRANT_VECTOR_SIZE` | Embedding dimension for all collections | `384` |
| `OLLAMA_HOST` | Ollama host (Docker service name) | `ollama` |
| `OLLAMA_PORT` | Ollama HTTP port | `11434` |
| `OLLAMA_URL` | Full Ollama URL (Docker network) | `http://ollama:11434` |
| `OLLAMA_MODEL` | Model to use (empty until Qwen 3 is installed) | *(empty)* |

> **Qdrant note:** `QDRANT_URL` must use the Docker service name (`qdrant`)
> inside the Docker network. Use `http://localhost:6333` only when running
> FastAPI locally on the host. Never commit a real `QDRANT_API_KEY` — when
> auth is enabled, the empty value in `.env.example` should be replaced locally.

> **Security:** Never commit `.env`. It is already in `.gitignore`. Use
> `.env.example` as a template with placeholder values only.

---

## Prerequisites

- **Docker** + **Docker Compose**
- **Python** 3.12+ (for local development)
- **Node.js** 22+ (for frontend)

---

## Start PostgreSQL

PostgreSQL runs as a Docker Compose service. To start only PostgreSQL:

```bash
docker compose up -d postgres
```

To verify PostgreSQL is healthy:

```bash
docker compose ps postgres
```

You should see `healthy` in the STATUS column.

---

## Start the Backend

The backend depends on PostgreSQL (and Qdrant/Ollama) being healthy. Start the
full stack:

```bash
docker compose up -d --build
```

Or start only the backend (after PostgreSQL is healthy):

```bash
docker compose up -d --build backend
```

The API will be available at `http://localhost:8000`.

---

## Start Qdrant

Qdrant runs as a Docker Compose service with a configured healthcheck, a
persistent `qdrant_storage` volume, HTTP/gRPC ports published (`6333`/`6334`),
and a restart policy. To start only Qdrant:

```bash
docker compose up -d qdrant
```

To verify Qdrant is healthy:

```bash
docker compose ps qdrant
```

You should see `healthy` in the STATUS column.

### Qdrant Dashboard

Qdrant ships an embedded web dashboard, accessible from the host at:

```
http://localhost:6333/dashboard
```

### Verify Qdrant Connectivity

From the host (port 6333 is published):

```bash
# REST API health endpoint
curl http://localhost:6333/healthz

# List existing collections
curl http://localhost:6333/collections
```

FastAPI → Qdrant over the Docker network (run inside the backend container):

```bash
# Full lifecycle verification (creates + removes a temporary collection only)
docker compose exec backend python scripts/verify_qdrant.py

# Automated tests (connectivity, create, insert, search, point/collection cleanup)
docker compose exec backend pytest tests/test_qdrant_connection.py -v
```

Both checks use `http://qdrant:6333` from inside the container — they never use
`localhost` for FastAPI-to-Qdrant communication. No destructive collection
operations are exposed through the public API; verification is limited to
internal scripts/tests working only on temporary collections.

---

## Ollama Architecture

Ollama runs as a **Docker Compose service** using the official `ollama/ollama`
image and serves the local LLM runtime. FastAPI talks to it over the Docker
network — never through `localhost`. Ollama is **not** installed as a separate
standalone process on the host; the container is the only installation.

```
app/ollama/
├── __init__.py      # Re-exports client/service helpers
├── config.py        # Centralized Ollama config (read from app.core.config)
├── client.py        # Centralized httpx AsyncClient creation (from config)
└── service.py       # OllamaService: check_connection, list_models, generate
```

- **Config** (`config.py`): reads `OLLAMA_URL` and `OLLAMA_MODEL` from the
  project's existing configuration system (`app/core/config.py`), which is
  populated from environment variables. No URL is hard-coded in source code.
- **Client** (`client.py`): builds an `httpx.AsyncClient` (async, so it never
  blocks the FastAPI event loop) from `OLLAMA_URL` and `OLLAMA_TIMEOUT`. A
  process-wide singleton is cached and closed on application shutdown.

---

## OpenClaw Integration

OpenClaw is used here as the installer/wrapper for the `cmdop` browser
automation runtime. The backend does not try to launch browser sessions during
startup; instead, it uses a small LangGraph workflow to detect whether the
runtime is installed and to report a clear status message.

The integration lives in [app/agents/openclaw.py](app/agents/openclaw.py) and
is verified by [tests/test_openclaw_integration.py](tests/test_openclaw_integration.py).

To run the standalone verification script:

```bash
python scripts/verify_openclaw.py
```

If the runtime is missing, install it first by running `openclaw` from a shell
on the machine where you want browser automation available.
- **Service** (`service.py`): reusable operations — `check_connection()`
  (hits `GET /api/tags`) and `list_models()`. A minimal `generate()` wrapper
  exists as a building block for later tasks, but no AI agent, RAG, prompt
  pipeline, or generation endpoint is built yet.
- **Health check** (`app/api/v1/endpoints/health.py`): `GET /api/v1/health`
  reports an `ollama` status alongside `database` and `qdrant`.

### Model storage

Models are persisted in the named Docker volume **`ollama_models`**, mounted at
`/root/.ollama` inside the container. Models are **never** stored only inside
the container filesystem — the volume survives container recreation.

### Docker configuration

| Item | Value |
|---|---|
| Image | `ollama/ollama:latest` |
| Port | `127.0.0.1:11434:11434` (published for local host access only) |
| Restart policy | `unless-stopped` |
| Volume | `ollama_models` → `/root/.ollama` |
| Network | `app-network` (shared bridge) |
| Container env | `OLLAMA_HOST=0.0.0.0` (container bind address) |
| Healthcheck | `ollama list` (uses the bundled CLI to verify the local API) |

> **Note on `OLLAMA_HOST`:** inside the Ollama *container*, `OLLAMA_HOST` is
> set to `0.0.0.0` so the server is reachable from the host and from other
> containers. The `OLLAMA_HOST=ollama` value in `.env` is the *backend-facing*
> Docker service name used to build `OLLAMA_URL` — the two are unrelated.

### Start Ollama

```bash
docker compose up -d ollama
```

To verify Ollama is healthy:

```bash
docker compose ps ollama
```

### Verify Ollama Connectivity

From the host (port 11434 is published only on loopback):

```bash
curl http://localhost:11434/api/tags
```

FastAPI → Ollama over the Docker network — run inside the backend container.
This is **mandatory** because it verifies Docker-network communication via the
`http://ollama:11434` URL (never `localhost`):

```bash
# Direct API probe from inside the backend container
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://ollama:11434/api/tags').read().decode())"

# Full verification script (uses httpx + the OllamaService)
docker compose exec backend python scripts/verify_ollama.py

# Automated tests (connectivity + expected empty model list)
docker compose exec backend pytest tests/test_ollama_connection.py -v
```

The model list is **expected to be empty** — no model is downloaded in this
task. No destructive Ollama management endpoints are exposed through the public
API; verification is limited to internal scripts/tests.

### CPU / GPU notes

Ollama is configured for **CPU by default** — there is no `deploy` GPU
reservation, so the stack runs on any machine. This host has no NVIDIA driver
or NVIDIA Container Toolkit, so GPU acceleration is intentionally **not**
enabled. To enable GPU later on a capable host, install the NVIDIA Container
Toolkit and uncomment the `deploy.resources` block in the `ollama` service in
`docker-compose.yml`, then run `docker compose up -d`. GPU support stays
optional and non-mandatory.

### Qwen 3

No Ollama model is downloaded in this task. **Qwen 3 will be installed in the
next task** (e.g. `docker compose exec ollama ollama pull qwen3:<tag>`). Once a
model is installed, set `OLLAMA_MODEL` in `.env` to the pulled model name so
the application configuration knows which model to use.

---

## Run Alembic Migrations

Alembic is configured to use the async PostgreSQL engine. Run migrations from
inside the backend container:

```bash
# Generate a new migration (after adding models)
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback one step
docker compose exec backend alembic downgrade -1

# Show current revision
docker compose exec backend alembic current
```

For local development (with PostgreSQL running in Docker):

```bash
alembic upgrade head
```

---

## Test Database Connectivity

Run the database connectivity tests (requires PostgreSQL container running):

```bash
# Inside the backend container
docker compose exec backend pytest tests/test_database_connection.py -v

# Or locally (with .env configured)
pytest tests/test_database_connection.py -v
```

The tests verify:
1. The SQLAlchemy async engine can connect to PostgreSQL (`SELECT 1`).
2. An `AsyncSession` can execute queries and return the current database name.

---

## Health Endpoint

The health endpoint verifies the API, PostgreSQL, Qdrant, and Ollama connectivity:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{"status": "ok", "api": "ok", "database": "ok", "qdrant": "ok", "ollama": "ok"}
```

If PostgreSQL is unreachable, `database` will be `"unavailable"`. If Qdrant is
unreachable, `qdrant` will be `"unavailable"`. If Ollama is unreachable,
`ollama` will be `"unavailable"`. The API response is always returned
(`status: "ok"` — the API itself is responsive) — component failures are
reported per dependency.

---

## Folder Structure

```
marketing-ai-agent/
├── app/                    # FastAPI backend
│   ├── api/                # HTTP routes (the "reception desk")
│   │   ├── deps.py         #   Shared dependencies (get_db_session)
│   │   ├── routes/         #   e.g. home.py
│   │   └── v1/             #   Versioned API endpoints
│   ├── agents/             # AI agent logic (e.g. MarketingAgent)
│   ├── core/               # App config & settings
│   ├── database/           # DB connections & session setup
│   ├── langchain/          # LangChain config, prompts, parsers, chains
│   ├── qdrant/             # Qdrant client, collections & service layer
│   ├── ollama/             # Ollama client, config & service layer
│   ├── middleware/         # Request middleware
│   ├── models/             # Database models (tables)
│   ├── prompts/            # LLM prompt templates
│   ├── schemas/            # Pydantic data contracts for the API
│   ├── services/           # Business logic layer
│   └── utils/              # Helper utilities
├── alembic/                # Database migrations
│   └── versions/           #   Migration scripts
├── frontend/               # React + TypeScript frontend (Vite)
├── scripts/                # Helper scripts
├── tests/                  # Automated tests
├── docs/                   # Documentation
└── docker/                 # Docker / container config
```

The LangChain layer is intentionally thin: it centralizes model settings,
prompt templates, output parsers, and reusable chain builders while reusing
the existing Ollama configuration.

---

## License

_Not specified yet._
