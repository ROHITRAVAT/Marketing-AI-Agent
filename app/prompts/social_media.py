"""Prompts for social media content creation."""

from app.prompts.base import PromptTemplate

SOCIAL_MEDIA_SYSTEM_PROMPT = (
    "You are an expert Social Media Manager.\n"
    "Your task is to take marketing content and adapt it into a highly engaging social media post.\n"
    "Tailor the tone, format, and length constraints appropriately for the specified platform.\n"
    "Include a clear Call to Action (CTA) and relevant hashtags.\n"
    "Output ONLY the social media post content without conversational filler."
)

SOCIAL_MEDIA_HUMAN_TEMPLATE = (
    "Please generate a social media post based on the following details:\n\n"
    "Platform: {platform}\n"
    "Target Audience: {target_audience}\n"
    "Product/Service: {product}\n"
    "Campaign Goal: {campaign_goal}\n\n"
    "Source Content:\n{generated_content}\n\n"
    "Write the optimized social media post now:"
)

social_media_template = PromptTemplate(
    name="social_media",
    system_prompt=SOCIAL_MEDIA_SYSTEM_PROMPT,
    human_template=SOCIAL_MEDIA_HUMAN_TEMPLATE,
    required_variables=[
        "platform",
        "target_audience",
        "product",
        "campaign_goal",
        "generated_content"
    ]
)
