import logging
import sys
import asyncio
from contextlib import asynccontextmanager

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import DBAPIError

from app.core.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS, LOG_LEVEL
from app.core.logging import setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
    database_exception_handler,
    marketing_agent_error_handler,
)
from app.core.errors import MarketingAgentError
from app.api.router import api_router
from app.api.routes.home import router as home_router
from app.database.connection import engine
from app.ollama.client import close_async_client as close_ollama_client
from app.qdrant.client import close_async_client as close_qdrant_client
from app.qdrant.service import ensure_qdrant_collections
from app.agents.checkpoint import setup_checkpointer
from app.scheduler.worker import run_scheduler, stop_scheduler

logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: setup on startup, cleanup on shutdown."""
    setup_logging(LOG_LEVEL)
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)
    import app.services.agent_service as agent_svc
    agent_svc._is_shutting_down = False
    try:
        result = await ensure_qdrant_collections()
        logger.info(
            "Qdrant collections ready — created: %s, already present: %s",
            result["created"],
            result["existing"],
        )
    except Exception as exc:  # pragma: no cover - operational fallback
        # Fail gracefully: the API still starts and /health reports degraded status.
        logger.info("Qdrant unavailable at startup, collection init skipped: %s", exc)

    try:
        await setup_checkpointer()
        logger.info("LangGraph checkpointer setup successful")
    except Exception as exc:
        logger.error("LangGraph checkpointer setup failed: %s", exc)

    try:
        from app.services.agent_service import AgentService
        from app.database.connection import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await AgentService.recover_stale_jobs(db)
        logger.info("Recovered stale agent jobs")
    except Exception as exc:
        logger.error("Failed to recover stale agent jobs: %s", exc)

    # Start the scheduler background task
    scheduler_task = asyncio.create_task(run_scheduler())

    yield
    
    # Gracefully shut down background agent tasks
    try:
        from app.services.agent_service import AgentService
        await AgentService.shutdown_background_tasks(timeout=5.0)
    except Exception as exc:
        logger.error("Error shutting down background agent tasks: %s", exc)

    # Gracefully stop the scheduler
    await stop_scheduler()
    try:
        await asyncio.wait_for(scheduler_task, timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Scheduler task did not stop gracefully within timeout.")
        scheduler_task.cancel()
    await engine.dispose()
    await close_qdrant_client()
    await close_ollama_client()
    logger.info("Shutting down %s", APP_NAME)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# Global exception handlers
app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DBAPIError, database_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Routers
app.include_router(api_router)
app.include_router(home_router)