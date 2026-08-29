"""Prompts for marketing campaign strategy and planning."""

from app.prompts.base import PromptTemplate

CAMPAIGN_STRATEGY_SYSTEM_PROMPT = (
    "You are a Senior Marketing Strategist.\n"
    "Your task is to analyze the provided product, target audience, platform, and campaign goal, "
    "along with the preliminary analysis, and develop a comprehensive marketing strategy.\n"
    "Your strategy should include positioning, key messaging themes, and actionable next steps.\n"
    "Output ONLY the strategy without conversational filler."
)

CAMPAIGN_STRATEGY_HUMAN_TEMPLATE = (
    "Please generate a marketing strategy based on the following details:\n\n"
    "Product/Service: {product}\n"
    "Target Audience: {target_audience}\n"
    "Platform: {platform}\n"
    "Campaign Goal: {campaign_goal}\n\n"
    "Preliminary Analysis:\n{analysis}\n\n"
    "Develop the marketing strategy now:"
)

campaign_strategy_template = PromptTemplate(
    name="campaign_strategy",
    system_prompt=CAMPAIGN_STRATEGY_SYSTEM_PROMPT,
    human_template=CAMPAIGN_STRATEGY_HUMAN_TEMPLATE,
    required_variables=[
        "product",
        "target_audience",
        "platform",
        "campaign_goal",
        "analysis"
    ]
)
