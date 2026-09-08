import pytest
from app.agents.graph import build_marketing_graph
from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus, ApprovalStatus

# We run these tests to validate E2E generation workflows
# They rely on the actual LangGraph node definitions and LLM calls.

pytestmark = pytest.mark.asyncio

@pytest.fixture
def graph():
    return build_marketing_graph()

async def run_scenario(graph, user_input: str, platform: str, product: str = "AI Marketing Platform", goal: str = "Launch") -> dict:
    state = MarketingAgentState(
        user_input=user_input,
        product=product,
        platform=platform,
        campaign_goal=goal,
        target_audience="Marketing Professionals",
        user_id=1,
    )
    # Invoke the full graph. We aren't configuring checkpointer here
    # but the node requires thread_id in config to persist approval requests.
    config = {"configurable": {"thread_id": "test-thread"}}
    result = await graph.ainvoke(state, config)
    return result

async def test_scenario_1_product_launch(graph):
    """Scenario 1 - Product Launch"""
    result = await run_scenario(graph, "Create a launch campaign for our new AI marketing platform.", "LinkedIn")
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
    assert result["strategy"] is not None
    assert len(result["plan"]) > 0
    assert result["generated_content"] is not None
    assert result["generated_content"].metadata["platform"].lower() == "linkedin"

async def test_scenario_2_linkedin_post(graph):
    """Scenario 2 — LinkedIn Post"""
    result = await run_scenario(graph, "Create a professional LinkedIn post announcing our new AI marketing product.", "LinkedIn")
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
    assert result["generated_content"] is not None

async def test_scenario_3_twitter_post(graph):
    """Scenario 3 — Twitter/X Post"""
    result = await run_scenario(graph, "Create a short Twitter/X post promoting our new product.", "Twitter/X")
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
    assert result["generated_content"] is not None

async def test_scenario_4_facebook_campaign(graph):
    """Scenario 4 — Facebook Campaign"""
    result = await run_scenario(graph, "Create a Facebook promotional post for our upcoming product launch.", "Facebook")
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
    assert result["generated_content"] is not None
    assert result["generated_content"].metadata["platform"].lower() == "facebook"

async def test_scenario_5_instagram_campaign(graph):
    """Scenario 5 — Instagram Campaign"""
    result = await run_scenario(graph, "Create an Instagram promotional post for our product launch.", "Instagram")
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
    assert result["generated_content"] is not None
    assert result["generated_content"].metadata["platform"].lower() == "instagram"

async def test_scenario_6_seo_content(graph):
    """Scenario 6 — SEO Content"""
    result = await run_scenario(graph, "Create an SEO-friendly blog topic and outline for AI marketing automation.", "Blog")
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
    assert result["generated_content"] is not None

async def test_scenario_8_content_regeneration(graph):
    """Scenario 8 — Content Regeneration"""
    from langchain_core.messages import HumanMessage, AIMessage
    # Simulate user requesting regeneration after a first response
    state = MarketingAgentState(
        user_input="Regenerate the previous post with a more professional tone.",
        platform="Facebook",
        product="AI Tool",
        target_audience="Developers",
        campaign_goal="Sales",
        conversation_history=[
            HumanMessage(content="Create a Facebook post about AI."),
            AIMessage(content="Here is your post: Hey guys, check out this cool AI tool!")
        ]
    )
    
    config = {"configurable": {"thread_id": "test-thread"}}
    result = await graph.ainvoke(state, config)
    assert result["generated_content"] is not None
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
