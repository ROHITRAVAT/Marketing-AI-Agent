from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.agent import AgentChatRequest, AgentChatJobResponse, AgentJobStatusResponse
from app.services.agent_service import AgentService
from fastapi import HTTPException

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post(
    "/chat",
    response_model=AgentChatJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Chat with the Marketing Agent",
    description="Send a message to the AI Marketing Agent. Returns a job ID that can be polled."
)
async def chat(
    request: AgentChatRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Execute the agent workflow for a given chat request in the background.
    """
    response = await AgentService.submit_chat_job(db, current_user.id, request)
    return response

@router.get(
    "/jobs/{job_id}",
    response_model=AgentJobStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Chat Job Status",
    description="Poll the status of a background chat job."
)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    job_status = await AgentService.get_job_status(db, job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status
