from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.enums import ToolExecutionStatus
from app.agents.schemas import ToolResult, ErrorInfo
from app.langchain.chains import (
    build_seo_chain,
    build_social_media_chain,
    build_ads_chain,
    build_email_marketing_chain,
    build_hashtag_chain,
)
from app.database.connection import AsyncSessionLocal
from app.models.approval import ApprovalRequest
from app.agents.enums import ApprovalStatus
from app.core.errors import ToolExecutionError, SocialMediaAPIError, ErrorCategory
from app.utils.retry import retry_operation
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def execute_tools(state: MarketingAgentState) -> dict:
    """
    Execute real tools for each planned step.

    Currently dispatches SEO and social-media generation to their real
    LangChain chains when a plan step's description mentions them.
    Implements idempotency and resilience to handle transient API errors.
    """

    logger.info("Executing tools...")

    try:
        new_tool_results: list[ToolResult] = []
        content_body = state.generated_content.body if state.generated_content else ""

        for step in state.plan or []:
            description_lower = step.description.lower()
            idempotency_key = f"approval_{state.approval_request_id or 'none'}_step_{step.step_id}"

            # Idempotency Check: if this exact step succeeded previously, skip it.
            existing_success = next(
                (tr for tr in state.tool_results if tr.idempotency_key == idempotency_key and tr.status == ToolExecutionStatus.SUCCESS),
                None
            )
            if existing_success:
                logger.info(f"Skipping already successful tool execution for {idempotency_key}")
                new_tool_results.append(existing_success)
                continue

            try:
                if "seo" in description_lower:
                    chain = build_seo_chain()
                    
                    async def run_seo():
                        return await chain.ainvoke({
                            "product": state.product or "",
                            "target_audience": state.target_audience or "",
                            "generated_content": content_body,
                        })

                    result = await retry_operation(
                        operation=run_seo,
                        max_attempts=3,
                        operation_name="seo_optimization"
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="seo_optimization",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result},
                        )
                    )

                elif "social" in description_lower:
                    # Verification checkpoint: ensure approval
                    if state.approval_required:
                        if not state.approval_request_id:
                            raise ToolExecutionError("Approval required but no request ID provided.", retryable=False)
                        
                        async with AsyncSessionLocal() as db:
                            result_db = await db.execute(
                                select(ApprovalRequest).where(ApprovalRequest.id == state.approval_request_id)
                            )
                            approval = result_db.scalar_one_or_none()
                            if not approval or approval.status != ApprovalStatus.APPROVED:
                                raise ToolExecutionError(f"Action not approved. Current status: {approval.status if approval else 'missing'}", retryable=False)
                    
                    chain = build_social_media_chain()
                    
                    async def run_social():
                        return await chain.ainvoke({
                            "post_count": "3",
                            "platform": state.platform or "",
                            "brief": state.user_input,
                            "audience": state.target_audience or "",
                            "goal": state.campaign_goal or "",
                        })

                    result = await retry_operation(
                        operation=run_social,
                        max_attempts=3,
                        operation_name="social_media_generation"
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="social_media_generation",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result},
                        )
                    )

                elif "ads" in description_lower:
                    chain = build_ads_chain()
                    
                    async def run_ads():
                        return await chain.ainvoke({
                            "product": state.product or "",
                            "target_audience": state.target_audience or "",
                            "campaign_goal": state.campaign_goal or "",
                            "platform": state.platform or "",
                            "generated_content": content_body,
                        })

                    result = await retry_operation(
                        operation=run_ads,
                        max_attempts=3,
                        operation_name="ads_generation"
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="ads_generation",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result},
                        )
                    )

                elif "email" in description_lower:
                    chain = build_email_marketing_chain()
                    
                    async def run_email():
                        return await chain.ainvoke({
                            "product": state.product or "",
                            "target_audience": state.target_audience or "",
                            "campaign_goal": state.campaign_goal or "",
                            "generated_content": content_body,
                        })

                    result = await retry_operation(
                        operation=run_email,
                        max_attempts=3,
                        operation_name="email_marketing_generation"
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="email_marketing_generation",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result},
                        )
                    )

                elif "campaign" in description_lower:
                    if not state.user_id:
                        raise ToolExecutionError(
                            "Cannot create campaign: no user_id on the agent state.",
                            retryable=False,
                        )

                    from app.services.campaign_service import CampaignService
                    from app.schemas.campaign import CampaignCreate

                    async def run_create_campaign():
                        campaign_in = CampaignCreate(
                            user_id=state.user_id,
                            name=state.product or state.campaign_goal or "Untitled Campaign",
                            description=(state.generated_content.body if state.generated_content else state.strategy) or "",
                            target_audience=state.target_audience,
                        )
                        async with AsyncSessionLocal() as db:
                            campaign = await CampaignService.create_campaign(db, campaign_in)
                            return {"campaign_id": campaign.id, "name": campaign.name}

                    result = await retry_operation(
                        operation=run_create_campaign,
                        max_attempts=3,
                        operation_name="create_campaign",
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="create_campaign",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result},
                        )
                    )

                elif "hashtag" in description_lower:
                    chain = build_hashtag_chain()

                    async def run_hashtags():
                        return await chain.ainvoke({
                            "platform": state.platform or "general",
                            "industry": state.target_audience or "",
                            "product": state.product or "",
                            "count": "10",
                        })

                    result = await retry_operation(
                        operation=run_hashtags,
                        max_attempts=3,
                        operation_name="hashtag_generation",
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="hashtag_generation",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result.model_dump() if hasattr(result, "model_dump") else result},
                        )
                    )

                else:
                    new_tool_results.append(
                        ToolResult(
                            tool_name=f"unmatched_step_{step.step_id}",
                            status=ToolExecutionStatus.FAILED,
                            idempotency_key=idempotency_key,
                            error=f"No tool implemented for step: {step.description}",
                            error_info=ErrorInfo(
                                error_code="TOOL_NOT_FOUND",
                                category=ErrorCategory.TOOL_ERROR.value,
                                message=f"No tool implemented for step: {step.description}",
                                retryable=False
                            )
                        )
                    )

            except Exception as tool_error:
                logger.error(f"Tool execution failed for {idempotency_key}: {tool_error}")
                
                # Determine retryability based on exception type
                retryable = getattr(tool_error, "retryable", False)
                error_code = getattr(tool_error, "error_code", "TOOL_EXEC_ERROR")
                category = getattr(tool_error, "category", ErrorCategory.TOOL_ERROR).value
                user_msg = getattr(tool_error, "user_message", str(tool_error))
                
                new_tool_results.append(
                    ToolResult(
                        tool_name=f"step_{step.step_id}",
                        status=ToolExecutionStatus.FAILED,
                        idempotency_key=idempotency_key,
                        error=str(tool_error),
                        error_info=ErrorInfo(
                            error_code=error_code,
                            category=category,
                            message=str(tool_error),
                            retryable=retryable,
                            user_message=user_msg
                        )
                    )
                )

        # We do not raise an exception here because the tests expect execute_tools
        # to return the structured results honestly. We can optionally set status if needed,
        # but to keep backward compatibility, we just return the tool_results.
        # If we need the error handler, we could set status = AgentStatus.FAILED here,
        # but the prompt says: "execute_tools should return a structured failure result
        # rather than raising ToolExecutionError and returning no state."


        return {
            "tool_results": new_tool_results,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "execute_tools",
        )