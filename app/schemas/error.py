from pydantic import BaseModel, Field

class APIErrorDetail(BaseModel):
    code: str = Field(..., description="Application-specific error code")
    message: str = Field(..., description="User-friendly error message")
    retryable: bool = Field(False, description="Whether the operation can be retried")

class APIErrorResponse(BaseModel):
    success: bool = Field(False, description="Always false for error responses")
    error: APIErrorDetail
