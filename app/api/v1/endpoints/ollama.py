from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.ollama.config import OLLAMA_SETTINGS
from app.ollama.service import OllamaService, get_ollama_service

router = APIRouter(prefix="/ollama", tags=["Ollama"])


class OllamaGenerateRequest(BaseModel):
    """Request payload for a single-turn Ollama generation call."""

    prompt: str = Field(..., min_length=1, description="Prompt text to send to the model")
    model: str | None = Field(default=None, description="Optional model override")
    system: str | None = Field(default=None, description="Optional system prompt")
    temperature: float | None = Field(default=None, description="Sampling temperature")
    options: dict[str, Any] | None = Field(
        default=None,
        description="Optional additional generation options passed directly to Ollama",
    )


class OllamaGenerateResponse(BaseModel):
    """Response returned after a successful Ollama inference call."""

    model: str
    response: str


@router.get("/models", response_model=list[dict[str, Any]], status_code=status.HTTP_200_OK)
async def list_ollama_models(
    ollama: OllamaService = Depends(get_ollama_service),
):
    """Return the models currently installed in Ollama."""
    try:
        return await ollama.list_models()
    except Exception as exc:  # pragma: no cover - service-specific failure path
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to list Ollama models: {exc}",
        ) from exc


@router.post(
    "/generate",
    response_model=OllamaGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate text via Ollama",
    description="Invokes the configured Ollama model and returns the generated response text.",
)
async def generate_ollama_response(
    payload: OllamaGenerateRequest,
    ollama: OllamaService = Depends(get_ollama_service),
):
    """Send a prompt to Ollama and return the generated completion."""
    extra_options: dict[str, Any] = {}
    if payload.system is not None:
        extra_options["system"] = payload.system
    if payload.temperature is not None:
        extra_options["temperature"] = payload.temperature
    if payload.options:
        extra_options.update(payload.options)

    try:
        response_text = await ollama.generate(
            payload.prompt,
            model=payload.model,
            **extra_options,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - network/server failure path
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama inference failed: {exc}",
        ) from exc

    model_name = payload.model or OLLAMA_SETTINGS.model
    return OllamaGenerateResponse(model=model_name, response=response_text)
