"""Reusable LangChain chain builders."""

from typing import Any, Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.langchain.llm import ChatOllama, get_chat_model
from app.langchain.parsers import JSON_OUTPUT_PARSER, TEXT_OUTPUT_PARSER
from app.langchain.prompts import (
    CAMPAIGN_STRATEGY_PROMPT,
    CONTENT_GENERATION_PROMPT,
    SOCIAL_MEDIA_PROMPT,
    SEO_OPTIMIZATION_PROMPT,
    ADS_PROMPT,
    EMAIL_MARKETING_PROMPT,
)

def build_ads_chain(model: ChatOllama | None = None) -> Any:
    """Convenience chain for generating ad copy."""

    return build_text_chain(prompt=ADS_PROMPT, model=model)


def build_email_marketing_chain(model: ChatOllama | None = None) -> Any:
    """Convenience chain for generating marketing emails."""

    return build_text_chain(prompt=EMAIL_MARKETING_PROMPT, model=model)

def build_seo_chain(model: ChatOllama | None = None) -> Any:
    """Convenience chain for generating SEO recommendations."""

    return build_text_chain(prompt=SEO_OPTIMIZATION_PROMPT, model=model)

def build_text_chain(
    prompt: ChatPromptTemplate = CONTENT_GENERATION_PROMPT,
    model: ChatOllama | None = None,
) -> Any:
    """Compose a prompt -> model -> string parser chain."""

    return prompt | (model or get_chat_model()) | TEXT_OUTPUT_PARSER


def build_json_chain(
    prompt: ChatPromptTemplate = CAMPAIGN_STRATEGY_PROMPT,
    model: ChatOllama | None = None,
) -> Any:
    """Compose a prompt -> model -> JSON parser chain."""

    return prompt | (model or get_chat_model()) | JSON_OUTPUT_PARSER


def build_structured_chain(
    schema: Type[BaseModel],
    prompt: ChatPromptTemplate = CAMPAIGN_STRATEGY_PROMPT,
    model: ChatOllama | None = None,
) -> Any:
    """Compose a prompt -> model (with structured output) chain."""
    llm = model or get_chat_model()
    # Ollama in langchain 0.3 supports with_structured_output using JSON schema mode.
    structured_llm = llm.with_structured_output(schema)
    return prompt | structured_llm


def build_social_media_chain(model: ChatOllama | None = None) -> Any:
    """Convenience chain for generating social media copy."""

    return build_text_chain(prompt=SOCIAL_MEDIA_PROMPT, model=model)
