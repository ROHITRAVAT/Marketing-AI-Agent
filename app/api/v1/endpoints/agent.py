from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post(
    "/chat",
    response_model=AgentChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the Marketing Agent",
    description="Send a message to the AI Marketing Agent to create or continue a conversation thread. Supports human-in-the-loop approval workflows and persistent memory."
)
async def chat(
    request: AgentChatRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Execute the agent workflow for a given chat request.
    """
    response = await AgentService.chat(db, current_user.id, request)
    return response
