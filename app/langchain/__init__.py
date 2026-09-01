"""LangChain integration for the Marketing AI Agent.

This package centralizes LangChain-specific configuration, reusable prompt
templates, output parsers, and chain builders so application code can stay
thin and focused on business logic.
"""

from app.langchain.chains import build_json_chain, build_text_chain
from app.langchain.config import LANGCHAIN_SETTINGS, LangChainSettings
from app.langchain.llm import build_chat_model, get_chat_model
from app.langchain.parsers import JSON_OUTPUT_PARSER, TEXT_OUTPUT_PARSER
from app.langchain.prompts import (
    CAMPAIGN_STRATEGY_PROMPT,
    CONTENT_GENERATION_PROMPT,
    SOCIAL_MEDIA_PROMPT,
)

__all__ = [
    "CAMPAIGN_STRATEGY_PROMPT",
    "CONTENT_GENERATION_PROMPT",
    "JSON_OUTPUT_PARSER",
    "LANGCHAIN_SETTINGS",
    "LangChainSettings",
    "SOCIAL_MEDIA_PROMPT",
    "TEXT_OUTPUT_PARSER",
    "build_chat_model",
    "build_json_chain",
    "build_text_chain",
    "get_chat_model",
]