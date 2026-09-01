"""Reusable LangChain prompt templates for marketing workflows."""

from langchain_core.prompts import ChatPromptTemplate


CAMPAIGN_STRATEGY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior marketing strategist. Produce concise, practical campaign guidance with clear next steps.",
        ),
        (
            "human",
            "Campaign brief:\n{campaign_brief}\n\nBrand context:\n{brand_context}\n\nOutput format:\n{output_format}",
        ),
    ]
)


CONTENT_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior copywriter for performance marketing. Write specific, conversion-focused content.",
        ),
        (
            "human",
            "Generate {content_type} for the following brief:\n\n{brief}\n\nTone:\n{tone}\n\nConstraints:\n{constraints}",
        ),
    ]
)


SOCIAL_MEDIA_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a social media strategist. Write platform-aware posts that feel natural and on-brand.",
        ),
        (
            "human",
            "Create {post_count} {platform} post options for this campaign:\n\n{brief}\n\nAudience:\n{audience}\n\nGoal:\n{goal}",
        ),
    ]
)