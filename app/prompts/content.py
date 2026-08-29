"""Prompts for marketing content generation."""

from app.prompts.base import PromptTemplate

CONTENT_GENERATION_SYSTEM_PROMPT = (
    "You are an expert Marketing AI Copywriter.\n"
    "Your goal is to write high-converting, engaging marketing content based "
    "on the provided strategy and campaign details.\n"
    "Adapt your writing style to suit the target platform and audience.\n"
    "Output ONLY the requested marketing content. Do not include introductory "
    "conversational text."
)

CONTENT_GENERATION_HUMAN_TEMPLATE = (
    "Please generate marketing content based on the following details:\n\n"
    "Product/Service: {product}\n"
    "Target Audience: {target_audience}\n"
    "Platform: {platform}\n"
    "Campaign Goal: {campaign_goal}\n\n"
    "Strategy:\n"
    "{strategy}\n\n"
    "Write the content now:"
)

marketing_content_template = PromptTemplate(
    name="content_generation",
    system_prompt=CONTENT_GENERATION_SYSTEM_PROMPT,
    human_template=CONTENT_GENERATION_HUMAN_TEMPLATE,
    required_variables=[
        "product",
        "target_audience",
        "platform",
        "campaign_goal",
        "strategy"
    ]
)
