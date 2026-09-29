from pydantic import BaseModel, Field
from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.langchain.chains import build_structured_chain
from langchain_core.prompts import ChatPromptTemplate
import asyncio

class RequestExtraction(BaseModel):
    product: str | None = Field(None, description="The product or service to promote")
    target_audience: str | None = Field(None, description="The target audience")
    platform: str | None = Field(None, description="The marketing platform (e.g., LinkedIn, Instagram, SEO)")
    campaign_goal: str | None = Field(None, description="The goal of the campaign (e.g., generate keywords, brand awareness)")

async def analyze_request(state: MarketingAgentState) -> dict:
    """
    Analyze the marketing request and return the analysis
    as a state update.
    """

    print("Analyzing marketing request...")

    try:
        if state.user_input:
            extraction_prompt = ChatPromptTemplate.from_messages([
                ("system", "Extract marketing campaign details from the user's input. If a detail is not explicitly mentioned or clearly implied, leave it as null. Note that requests like 'Suggest targeted SEO keywords for B2B SaaS' implies product='B2B SaaS', platform='SEO', campaign_goal='Suggest targeted SEO keywords'."),
                ("human", "{user_input}")
            ])
            chain = build_structured_chain(schema=RequestExtraction, prompt=extraction_prompt)
            result = await chain.ainvoke({"user_input": state.user_input})
            
            # Update state variables if extracted
            if result.product and not state.product:
                state.product = result.product
            if result.target_audience and not state.target_audience:
                state.target_audience = result.target_audience
            if result.platform and not state.platform:
                state.platform = result.platform
            if result.campaign_goal and not state.campaign_goal:
                state.campaign_goal = result.campaign_goal

        required_fields = {
            "product": "product or service",
            "target_audience": "target audience",
            "platform": "marketing platform",
            "campaign_goal": "campaign goal",
        }

        missing_fields = []

        for field, description in required_fields.items():
            if not getattr(state, field):
                missing_fields.append(description)

        if missing_fields:
            analysis = (
                "The marketing request is incomplete. "
                "The following information is missing: "
                + ", ".join(missing_fields)
                + "."
            )
        else:
            analysis = (
                f"The user wants to create a {state.platform} campaign "
                f"for {state.product}, targeting "
                f"{state.target_audience}, with the goal of "
                f"{state.campaign_goal}."
            )

        return {
            "analysis": analysis,
            "product": state.product,
            "target_audience": state.target_audience,
            "platform": state.platform,
            "campaign_goal": state.campaign_goal,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "analyze_request",
        )