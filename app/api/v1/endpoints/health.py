from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.ollama.service import OllamaService, get_ollama_service
from app.qdrant.service import QdrantService, get_qdrant_service

router = APIRouter()


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db_session),
    qdrant: QdrantService = Depends(get_qdrant_service),
    ollama: OllamaService = Depends(get_ollama_service),
):
    """Health check verifying API, PostgreSQL, Qdrant, and Ollama connectivity.

    The response is always returned with ``status: "ok"`` (the API itself is
    responsive). Individual component failures are reported per dependency as
    ``"ok"`` or ``"unavailable"``.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"

    try:
        await qdrant.check_connection()
        qdrant_status = "ok"
    except Exception:
        qdrant_status = "unavailable"

    try:
        await ollama.check_connection()
        ollama_status = "ok"
    except Exception:
        ollama_status = "unavailable"

    return {
        "status": "ok",
        "api": "ok",
        "database": db_status,
        "qdrant": qdrant_status,
        "ollama": ollama_status,
    }