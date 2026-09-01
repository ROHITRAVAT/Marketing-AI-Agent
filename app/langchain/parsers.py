"""Reusable LangChain output parsers."""

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser


TEXT_OUTPUT_PARSER = StrOutputParser()
JSON_OUTPUT_PARSER = JsonOutputParser()