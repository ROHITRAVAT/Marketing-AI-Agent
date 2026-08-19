from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.prompt import (
    PromptCreate,
    PromptListResponse,
    PromptResponse,
    PromptType,
    PromptUpdate,
)
from app.schemas.common import SuccessResponse
from app.services.prompt_service import PromptService

router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.post(
    "/",
    response_model=PromptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a prompt template",
    description="Creates a new AI prompt template with optional campaign linkage and parameter variables.",
)
async def create_prompt(
    prompt_in: PromptCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new prompt template."""
    try:
        return await PromptService.create_prompt(db, prompt_in)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prompt: {str(err)}",
        )


@router.get(
    "/",
    response_model=PromptListResponse,
    status_code=status.HTTP_200_OK,
    summary="List prompt templates",
    description="Retrieves a paginated list of prompt templates with optional filters for user_id, campaign_id, prompt_type, and search query.",
)
async def list_prompts(
    user_id: Optional[int] = Query(None, description="Filter by owner user ID"),
    campaign_id: Optional[int] = Query(None, description="Filter by associated campaign ID"),
    prompt_type: Optional[PromptType] = Query(None, description="Filter by prompt type"),
    search: Optional[str] = Query(None, description="Search in prompt title or template text"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    db: AsyncSession = Depends(get_db_session),
):
    """List prompt templates with pagination and filtering."""
    skip = (page - 1) * size
    items, total = await PromptService.get_prompts(
        db,
        user_id=user_id,
        campaign_id=campaign_id,
        prompt_type=prompt_type,
        search=search,
        skip=skip,
        limit=size,
    )
    return PromptListResponse(
        total=total,
        page=page,
        size=size,
        items=[PromptResponse.model_validate(item) for item in items],
    )


@router.get(
    "/{prompt_id}",
    response_model=PromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Get prompt template by ID",
    description="Retrieves a single prompt template by its unique integer ID.",
)
async def get_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a prompt template by ID."""
    prompt = await PromptService.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_id} not found",
        )
    return prompt


@router.put(
    "/{prompt_id}",
    response_model=PromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Update prompt template",
    description="Updates attributes of an existing prompt template.",
)
async def update_prompt(
    prompt_id: int,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update a prompt template by ID."""
    try:
        updated = await PromptService.update_prompt(db, prompt_id, prompt_in)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_id} not found",
        )
    return updated


@router.patch(
    "/{prompt_id}",
    response_model=PromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update prompt template",
    description="Partially updates specified attributes of a prompt template.",
)
async def patch_prompt(
    prompt_id: int,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Partially update a prompt template by ID."""
    try:
        updated = await PromptService.update_prompt(db, prompt_id, prompt_in)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_id} not found",
        )
    return updated


@router.delete(
    "/{prompt_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete prompt template",
    description="Deletes a prompt template by ID.",
)
async def delete_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a prompt template by ID."""
    deleted = await PromptService.delete_prompt(db, prompt_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_id} not found",
        )
    return SuccessResponse(
        success=True,
        message=f"Prompt {prompt_id} successfully deleted",
        data={"id": prompt_id},
    )
