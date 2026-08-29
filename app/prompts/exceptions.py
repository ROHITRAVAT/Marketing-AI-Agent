"""Custom exceptions for the Prompt Template Library."""

class PromptError(Exception):
    """Base class for prompt-related exceptions."""
    pass

class PromptNotFoundError(PromptError):
    """Raised when a requested prompt template cannot be found."""
    pass

class PromptValidationError(PromptError):
    """Raised when a prompt template is invalid or missing required variables."""
    pass
