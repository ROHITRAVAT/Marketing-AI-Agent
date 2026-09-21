"""LLM wrappers backed by LangChain and Ollama."""

from functools import lru_cache

from langchain_ollama import ChatOllama

from app.langchain.config import LANGCHAIN_SETTINGS


def build_chat_model(
    model: str | None = None,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
) -> ChatOllama:
    """Create a configured LangChain chat model for the Ollama backend."""

    model_name = model or LANGCHAIN_SETTINGS.model
    if not model_name:
        raise ValueError(
            "No Ollama model configured. Set OLLAMA_MODEL before building a LangChain chat model."
        )

    return ChatOllama(
        base_url=LANGCHAIN_SETTINGS.base_url,
        model=model_name,
        temperature=LANGCHAIN_SETTINGS.temperature if temperature is None else temperature,
        num_predict=LANGCHAIN_SETTINGS.max_tokens if max_tokens is None else max_tokens,
        top_p=LANGCHAIN_SETTINGS.top_p if top_p is None else top_p,
        top_k=LANGCHAIN_SETTINGS.top_k if top_k is None else top_k,
    )


@lru_cache(maxsize=1)
def get_chat_model() -> ChatOllama:
    """Return the process-wide default LangChain chat model."""

    return build_chat_model()