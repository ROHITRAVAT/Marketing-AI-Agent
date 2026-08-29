from typing import TypedDict


class MarketingAgentState(TypedDict):
    user_id: int
    user_request: str
    product: str
    target_audience: str
    platform: str
    campaign_goal: str
    analysis: str
    strategy: str
    generated_content: str
    clarification_message: str
    status: str
    error_message: str