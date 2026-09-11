"""Reusable LangChain prompt templates for marketing workflows."""

from langchain_core.prompts import ChatPromptTemplate


CAMPAIGN_STRATEGY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior marketing strategist. Produce concise, practical campaign guidance with clear next steps. "
            "Use the retrieved knowledge and brand context where available. Avoid making unsupported claims or inventing facts."
        ),
        (
            "human",
            "Campaign brief:\n{campaign_brief}\n\nTarget Audience:\n{target_audience}\n\nCampaign Goal:\n{campaign_goal}\n\nBrand context:\n{brand_context}\n\nRetrieved Knowledge:\n{retrieved_knowledge}\n\nOutput format:\n{output_format}",
        ),
    ]
)


CONTENT_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior copywriter for performance marketing. Write specific, conversion-focused content. "
            "Use the provided strategy, plan, and retrieved context. Avoid inventing company facts."
        ),
        (
            "human",
            "Generate {content_type} for the following platform: {platform}\n\n"
            "Audience:\n{audience}\n\n"
            "Tone:\n{tone}\n\n"
            "Brief/Request:\n{brief}\n\n"
            "Strategy:\n{strategy}\n\n"
            "Execution Plan:\n{plan}\n\n"
            "Retrieved Context:\n{retrieved_context}\n\n"
            "Constraints:\n{constraints}",
        ),
    ]
)


SOCIAL_MEDIA_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a social media strategist. Write platform-aware posts that feel natural and on-brand. "
            "Use retrieved knowledge when available. Follow platform-specific requirements."
        ),
        (
            "human",
            "Create {post_count} {platform} post options for this campaign:\n\n"
            "Brief:\n{brief}\n\n"
            "Strategy:\n{strategy}\n\n"
            "Audience:\n{audience}\n\n"
            "Goal:\n{goal}\n\n"
            "Retrieved Context:\n{retrieved_context}",
        ),
    ]
)


PLANNING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a marketing execution planner. Convert the provided strategy into structured plan steps. "
            "Return a JSON object containing a list of plan steps with keys 'step_id' and 'description'."
        ),
        (
            "human",
            "Strategy:\n{strategy}\n\nGoal:\n{campaign_goal}\n\nPlatform:\n{platform}",
        ),
    ]
)


REVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a marketing QA reviewer. Evaluate the generated content for relevance, clarity, quality, and factual consistency. "
            "Return a JSON object with keys: 'approved' (boolean), 'score' (0-10 float), 'feedback' (string), and 'issues' (list of strings)."
        ),
        (
            "human",
            "Strategy:\n{strategy}\n\nPlan:\n{plan}\n\nGenerated Content:\n{content}\n\nPlatform:\n{platform}\n\nAudience:\n{audience}",
        ),
    ]
)

SEO_OPTIMIZATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert SEO specialist. Analyze marketing content and produce SEO recommendations: "
            "5 targeted keywords, an optimized title, a meta description under 160 characters, and heading suggestions. "
            "Output ONLY the requested SEO information without introductory filler.",
        ),
        (
            "human",
            "Product/Service: {product}\nTarget Audience: {target_audience}\n\n"
            "Marketing Content:\n{generated_content}\n\nProvide SEO recommendations now:",
        ),
    ]
)

ADS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a performance ads copywriter. Write concise, high-converting ad copy "
            "with a strong hook and clear call-to-action, respecting platform character limits.",
        ),
        (
            "human",
            "Product/Service: {product}\nPlatform: {platform}\nTarget Audience: {audience}\n\n"
            "Campaign Goal: {campaign_goal}\n\nWrite the ad copy now:",
        ),
    ]
)

EMAIL_MARKETING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an email marketing specialist. Write an engaging marketing email with a "
            "compelling subject line, clear body copy, and a single strong call-to-action.",
        ),
        (
            "human",
            "Product/Service: {product}\nTarget Audience: {audience}\nCampaign Goal: {campaign_goal}\n\n"
            "Source Content:\n{generated_content}\n\nWrite the subject line and email body now:",
        ),
    ]
)

HASHTAG_GENERATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a social media hashtag strategist. Generate relevant, high-reach hashtags "
            "tailored to the platform and industry, mixing broad and niche tags for discoverability.",
        ),
        (
            "human",
            "Platform: {platform}\nIndustry: {industry}\nTopic/Product: {product}\n"
            "Number of hashtags: {count}\n\nGenerate the hashtags now:",
        ),
    ]
)

CAMPAIGN_GENERATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior marketing strategist. Produce a complete, structured campaign plan "
            "with clear audience targeting, messaging, channels, and success metrics.",
        ),
        (
            "human",
            "Campaign objective: {campaign_goal}\nProduct/Service: {product}\n"
            "Target Audience: {target_audience}\nPlatform: {platform}\n\n"
            "Generate the complete campaign now:",
        ),
    ]
)