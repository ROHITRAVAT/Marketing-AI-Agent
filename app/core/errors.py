from enum import Enum
from typing import Any

class ErrorCategory(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    LLM_ERROR = "LLM_ERROR"
    TOOL_ERROR = "TOOL_ERROR"
    TOOL_OUTPUT_ERROR = "TOOL_OUTPUT_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"
    API_ERROR = "API_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    WORKFLOW_ERROR = "WORKFLOW_ERROR"
    CHECKPOINT_ERROR = "CHECKPOINT_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class MarketingAgentError(Exception):
    """Base exception for all Marketing AI Agent errors."""
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        error_code: str,
        retryable: bool = False,
        user_message: str | None = None,
        original_exception: Exception | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.error_code = error_code
        self.retryable = retryable
        self.user_message = user_message or "An unexpected error occurred."
        self.original_exception = original_exception
        self.metadata = metadata or {}

class LLMTimeoutError(MarketingAgentError):
    def __init__(self, message: str = "LLM service timed out", original_exception: Exception | None = None):
        super().__init__(
            message=message,
            category=ErrorCategory.TIMEOUT_ERROR,
            error_code="LLM_TIMEOUT",
            retryable=True,
            user_message="The AI generation service is taking too long to respond. Please try again.",
            original_exception=original_exception
        )

class LLMValidationError(MarketingAgentError):
    def __init__(self, message: str = "LLM returned invalid structured output", original_exception: Exception | None = None):
        super().__init__(
            message=message,
            category=ErrorCategory.LLM_ERROR,
            error_code="LLM_VALIDATION_FAILED",
            retryable=True, # Often we want to retry generation
            user_message="The AI generated invalid content. Attempting to regenerate.",
            original_exception=original_exception
        )

class ToolExecutionError(MarketingAgentError):
    def __init__(self, message: str, retryable: bool = False, original_exception: Exception | None = None):
        super().__init__(
            message=message,
            category=ErrorCategory.TOOL_ERROR,
            error_code="TOOL_EXECUTION_FAILED",
            retryable=retryable,
            user_message="An external action failed.",
            original_exception=original_exception
        )

class SocialMediaAPIError(MarketingAgentError):
    def __init__(self, message: str, error_code: str, retryable: bool = False, user_message: str | None = None, original_exception: Exception | None = None, metadata: dict | None = None):
        super().__init__(
            message=message,
            category=ErrorCategory.API_ERROR,
            error_code=error_code,
            retryable=retryable,
            user_message=user_message or "Unable to publish to social media.",
            original_exception=original_exception,
            metadata=metadata
        )

class DatabaseTransientError(MarketingAgentError):
    def __init__(self, message: str = "Database connection failed temporarily", original_exception: Exception | None = None):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE_ERROR,
            error_code="DB_TRANSIENT_ERROR",
            retryable=True,
            user_message="Experiencing temporary database issues.",
            original_exception=original_exception
        )

class WorkflowStateError(MarketingAgentError):
    def __init__(self, message: str, original_exception: Exception | None = None):
        super().__init__(
            message=message,
            category=ErrorCategory.WORKFLOW_ERROR,
            error_code="WORKFLOW_INVALID_STATE",
            retryable=False,
            user_message="The workflow encountered an unexpected state and cannot continue.",
            original_exception=original_exception
        )

class QdrantTransientError(MarketingAgentError):
    def __init__(self, message: str = "Vector DB temporarily unavailable", original_exception: Exception | None = None):
        super().__init__(
            message=message,
            category=ErrorCategory.VECTOR_DB_ERROR,
            error_code="QDRANT_TRANSIENT_ERROR",
            retryable=True,
            user_message="Temporary issue retrieving context.",
            original_exception=original_exception
        )
