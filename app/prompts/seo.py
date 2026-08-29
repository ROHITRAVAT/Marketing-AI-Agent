"""Prompts for SEO optimization and keyword generation."""

from app.prompts.base import PromptTemplate

SEO_OPTIMIZATION_SYSTEM_PROMPT = (
    "You are an expert SEO Specialist.\n"
    "Your task is to analyze the provided marketing content and generate SEO recommendations.\n"
    "Provide a list of 5 targeted keywords, an optimized SEO title, a meta description (under 160 characters), "
    "and suggestions for heading placements to maximize search engine visibility.\n"
    "Output ONLY the requested SEO information without introductory filler."
)

SEO_OPTIMIZATION_HUMAN_TEMPLATE = (
    "Please generate SEO recommendations for the following details:\n\n"
    "Product/Service: {product}\n"
    "Target Audience: {target_audience}\n\n"
    "Marketing Content:\n{generated_content}\n\n"
    "Provide the SEO title, meta description, keywords, and heading recommendations now:"
)

seo_optimization_template = PromptTemplate(
    name="seo_optimization",
    system_prompt=SEO_OPTIMIZATION_SYSTEM_PROMPT,
    human_template=SEO_OPTIMIZATION_HUMAN_TEMPLATE,
    required_variables=[
        "product",
        "target_audience",
        "generated_content"
    ]
)
