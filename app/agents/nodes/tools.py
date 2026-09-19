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
    build_campaign_generator_chain,
    build_content_calendar_chain,
    build_campaign_optimization_chain,
)
import app.database.connection as db_conn
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
    print("Executing tools...")

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

                elif any(
                    keyword in description_lower
                    for keyword in ["social", "linkedin", "facebook", "instagram", "twitter", " x post", "x.com"]
                ):
                    # Verification checkpoint: ensure approval
                    if state.approval_required:
                        if not state.approval_request_id:
                            raise ToolExecutionError("Approval required but no request ID provided.", retryable=False)
                        
                        async with db_conn.AsyncSessionLocal() as db:
                            result_db = await db.execute(
                                select(ApprovalRequest).where(ApprovalRequest.id == state.approval_request_id)
                            )
                            approval = result_db.scalar_one_or_none()
                            if not approval or approval.status != ApprovalStatus.APPROVED:
                                raise ToolExecutionError(f"Action not approved. Current status: {approval.status if approval else 'missing'}", retryable=False)
                    
                    platform = (state.platform or "").lower()
                    if platform not in ("linkedin", "facebook", "instagram", "twitter", "twitter/x"):
                        # Try to infer from step description
                        if "linkedin" in description_lower:
                            platform = "linkedin"
                        elif "facebook" in description_lower:
                            platform = "facebook"
                        elif "instagram" in description_lower:
                            platform = "instagram"
                        elif "twitter" in description_lower or " x " in description_lower:
                            platform = "twitter"

                    if platform in ("linkedin", "facebook", "instagram", "twitter", "twitter/x"):
                        from app.models.scheduled_post import ScheduledPost
                        from datetime import datetime, timezone
                        
                        post_id = None
                        
                        if platform == "linkedin":
                            from app.services.linkedin_service import LinkedInService
                            async with db_conn.AsyncSessionLocal() as db:
                                post_id = await LinkedInService.publish_post(
                                    user_id=state.user_id,
                                    content=content_body,
                                    db=db
                                )
                        elif platform == "facebook":
                            from app.services.facebook_service import FacebookService
                            async with db_conn.AsyncSessionLocal() as db:
                                post_id = await FacebookService.publish_post(
                                    user_id=state.user_id,
                                    content=content_body,
                                    db=db
                                )
                        elif platform == "instagram":
                            from app.services.instagram_service import InstagramService
                            image_url = None
                            if state.generated_content and state.generated_content.metadata:
                                image_url = state.generated_content.metadata.get("image_url")
                            async with db_conn.AsyncSessionLocal() as db:
                                post_id = await InstagramService.publish_post(
                                    user_id=state.user_id,
                                    caption=content_body,
                                    image_url=image_url,
                                    db=db
                                )
                        elif platform in ("twitter", "twitter/x"):
                            from app.services.twitter_service import TwitterService
                            async with db_conn.AsyncSessionLocal() as db:
                                post_id = await TwitterService.publish_post(
                                    user_id=state.user_id,
                                    content=content_body,
                                    db=db
                                )

                        # Create a ScheduledPost so analytics can track it!
                        image_url = None
                        if platform == "instagram" and state.generated_content and state.generated_content.metadata:
                            image_url = state.generated_content.metadata.get("image_url")
                        media_urls = [image_url] if image_url else None
                        
                        async with db_conn.AsyncSessionLocal() as db:
                            from app.core.oauth.manager import TokenManager
                            connection = await TokenManager.get_connection_status(state.user_id, platform, db)
                            account_id = connection.provider_user_id if connection else None
                            if platform == "linkedin" and account_id:
                                account_id = f"urn:li:person:{account_id}"

                            new_post = ScheduledPost(
                                user_id=state.user_id,
                                platform="twitter" if platform == "twitter/x" else platform,
                                content=content_body,
                                media_urls=media_urls,
                                scheduled_time=datetime.now(timezone.utc),
                                status="published",
                                external_post_id=post_id,
                                account_id=account_id,
                                published_at=datetime.now(timezone.utc),
                                approval_request_id=state.approval_request_id
                            )
                            db.add(new_post)
                            await db.commit()
                            await db.refresh(new_post)
                            db_post_id = new_post.id
                        
                        new_tool_results.append(
                            ToolResult(
                                tool_name=f"{platform}_publish",
                                status=ToolExecutionStatus.SUCCESS,
                                idempotency_key=idempotency_key,
                                data={"output": f"Post published successfully for {platform}. DB ID: {db_post_id} External ID: {post_id}"},
                            )
                        )
                    else:
                        # Fallback to general social media generator if platform is missing
                        chain = build_social_media_chain()
                        
                        async def run_social():
                            return await chain.ainvoke({
                                "post_count": "3",
                                "platform": state.platform or "",
                                "brief": state.user_input,
                                "strategy": state.strategy or "",
                                "audience": state.target_audience or "",
                                "goal": state.campaign_goal or "",
                                "retrieved_context": "\n\n".join(
                                    doc.content for doc in state.retrieved_documents
                                ) if state.retrieved_documents else "No additional knowledge retrieved.",
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

                elif "generate" in description_lower and "campaign" in description_lower:
                    chain = build_campaign_generator_chain()

                    async def run_campaign_generator():
                        return await chain.ainvoke({
                            "campaign_goal": state.campaign_goal or "",
                            "product": state.product or "",
                            "target_audience": state.target_audience or "",
                            "platform": state.platform or "",
                        })

                    result = await retry_operation(
                        operation=run_campaign_generator,
                        max_attempts=3,
                        operation_name="campaign_generator",
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="campaign_generator",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result.model_dump() if hasattr(result, "model_dump") else result},
                        )
                    )

                elif "optimiz" in description_lower:
                    if not state.campaign_id:
                        raise ToolExecutionError(
                            "Cannot optimize campaign: no campaign_id on the agent state.",
                            retryable=False,
                        )

                    from app.services.campaign_service import CampaignService

                    async def run_campaign_optimization():
                        async with db_conn.AsyncSessionLocal() as db:
                            campaign = await CampaignService.get_campaign(db, state.campaign_id)
                            if not campaign:
                                raise ToolExecutionError(
                                    f"Campaign {state.campaign_id} not found.",
                                    retryable=False,
                                )

                            chain = build_campaign_optimization_chain()
                            analysis = await chain.ainvoke({
                                "campaign_name": campaign.name,
                                "description": campaign.description or "",
                                "target_audience": campaign.target_audience or "",
                                "status": campaign.status,
                                "budget": str(campaign.budget) if campaign.budget else "Not specified",
                            })
                            return analysis.model_dump() if hasattr(analysis, "model_dump") else analysis

                    result = await retry_operation(
                        operation=run_campaign_optimization,
                        max_attempts=3,
                        operation_name="campaign_optimization",
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="campaign_optimization",
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
                        async with db_conn.AsyncSessionLocal() as db:
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

                elif "calendar" in description_lower or "schedule" in description_lower:
                    chain = build_content_calendar_chain()

                    async def run_calendar():
                        return await chain.ainvoke({
                            "product": state.product or "",
                            "target_audience": state.target_audience or "",
                            "platform": state.platform or "",
                            "campaign_goal": state.campaign_goal or "",
                            "timeframe": "weekly",
                        })

                    result = await retry_operation(
                        operation=run_calendar,
                        max_attempts=3,
                        operation_name="content_calendar",
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="content_calendar",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result.model_dump() if hasattr(result, "model_dump") else result},
                        )
                    )

                elif "analytic" in description_lower:
                    from app.agents.tools.analytics_tool import get_analytics_summary_for_agent
                    
                    async def run_analytics():
                        async with db_conn.AsyncSessionLocal() as db:
                            return await get_analytics_summary_for_agent(
                                user_id=state.user_id,
                                db=db,
                                days=30
                            )
                            
                    result = await retry_operation(
                        operation=run_analytics,
                        max_attempts=3,
                        operation_name="analytics_retrieval"
                    )

                    new_tool_results.append(
                        ToolResult(
                            tool_name="analytics_retrieval",
                            status=ToolExecutionStatus.SUCCESS,
                            idempotency_key=idempotency_key,
                            data={"output": result},
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