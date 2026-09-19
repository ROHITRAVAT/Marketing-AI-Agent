import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.scheduled_post import ScheduledPost
from app.models.approval import ApprovalRequest
from app.agents.enums import ApprovalStatus, ToolExecutionStatus
from app.agents.state import MarketingAgentState
from app.agents.schemas import GeneratedContent, PlanStep, ToolResult
from app.agents.nodes.tools import execute_tools
from app.core.config import SCHEDULER_MAX_RETRIES

logger = logging.getLogger(__name__)

async def process_scheduled_post(post: ScheduledPost, db: AsyncSession) -> None:
    """
    Executes a scheduled post by verifying its approval status, synthesizing a 
    MarketingAgentState, and invoking the core execute_tools logic.
    """
    logger.info(f"Processing scheduled post {post.id} for platform {post.platform}")

    # 1. Verification
    if post.approval_request_id:
        result = await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == post.approval_request_id))
        approval = result.scalar_one_or_none()
        
        if not approval or approval.status != ApprovalStatus.APPROVED:
            post.status = "failed"
            post.error_message = f"Post rejected or approval missing. Current status: {approval.status if approval else 'None'}"
            post.updated_at = datetime.now(timezone.utc)
            await db.commit()
            logger.warning(f"Scheduled post {post.id} failed verification: {post.error_message}")
            return

    # 2. State Construction
    # Build a minimal synthetic state to satisfy execute_tools
    image_url = None
    if post.media_urls and len(post.media_urls) > 0:
        image_url = post.media_urls[0]

    synthetic_state = MarketingAgentState(
        user_id=post.user_id,
        user_input=f"Scheduled post for {post.platform}",
        platform=post.platform,
        approval_required=True if post.approval_request_id else False,
        approval_request_id=post.approval_request_id,
        generated_content=GeneratedContent(
            content_type="social_post",
            body=post.content or "",
            metadata={"image_url": image_url} if image_url else {}
        ),
        plan=[
            PlanStep(step_id="1", description=f"Publish social post to {post.platform}")
        ]
    )

    # 3. Execution
    post.attempt_count += 1
    post.last_attempt_at = datetime.now(timezone.utc)
    
    try:
        result_dict = await execute_tools(synthetic_state)
        tool_results: list[ToolResult] = result_dict.get("tool_results", [])
        
        # 4. Result Handling
        if tool_results and tool_results[0].status == ToolExecutionStatus.SUCCESS:
            post.status = "published"
            post.published_at = datetime.now(timezone.utc)
            
            # Try to extract post/media ID from the tool output
            output = tool_results[0].data.get("output", "")
            if "External ID: " in output:
                post.external_post_id = output.split("External ID: ")[1].strip()
            elif "Post ID: " in output:
                post.external_post_id = output.split("Post ID: ")[1].strip()
            elif "Media ID: " in output:
                post.external_post_id = output.split("Media ID: ")[1].strip()
                
            post.error_message = None
            logger.info(f"Scheduled post {post.id} published successfully.")
            await db.commit()
        else:
            # Tool executed but didn't return success explicitly (or returned error)
            error_data = tool_results[0].data if tool_results else "Unknown error"
            raise Exception(f"Tool execution did not report success: {error_data}")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to publish scheduled post {post.id}: {error_msg}")
        
        # Check if it's a temporary error that we should retry
        # In a real system, you might inspect the exception type (e.g., rate limit, 5xx).
        # We will assume by default it's retryable up to MAX_RETRIES unless it's a known permanent error.
        
        is_permanent = False
        if "Action not approved" in error_msg or "Approval required" in error_msg:
            is_permanent = True
            
        if is_permanent or post.attempt_count >= SCHEDULER_MAX_RETRIES:
            post.status = "failed"
            post.error_message = error_msg
        else:
            # Leave it as scheduled for the next sweep
            post.status = "scheduled"
            post.error_message = f"Attempt {post.attempt_count} failed: {error_msg}"
            # A real backoff could bump `scheduled_time` here, but for simplicity we rely on the next polling cycle.

    post.updated_at = datetime.now(timezone.utc)
    await db.commit()
