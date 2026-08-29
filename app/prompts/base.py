"""Base classes and types for prompt templates."""

import logging
from dataclasses import dataclass, field
from app.prompts.exceptions import PromptValidationError

logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate:
    """A reusable prompt template with validation."""
    
    name: str
    system_prompt: str
    human_template: str
    required_variables: list[str] = field(default_factory=list)

    def render(self, **kwargs) -> str:
        """Render the prompt template with the provided variables.
        
        Args:
            **kwargs: Variables to inject into the human template.
            
        Returns:
            A formatted prompt string suitable for the LLM.
            
        Raises:
            PromptValidationError: If required variables are missing or invalid.
        """
        # Validate that all required variables are present, not None, and not empty strings
        missing_vars = []
        for var in self.required_variables:
            val = kwargs.get(var)
            if val is None or str(val).strip() == "":
                missing_vars.append(var)
                
        if missing_vars:
            error_msg = f"Missing required variables for template '{self.name}': {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise PromptValidationError(error_msg)

        # Attempt to render the template
        try:
            rendered_human = self.human_template.format(**kwargs)
        except KeyError as e:
            error_msg = f"Template '{self.name}' expects variable '{e.args[0]}' in the human_template but it was not provided."
            logger.error(error_msg)
            raise PromptValidationError(error_msg) from e
        except Exception as e:
            logger.error("Failed to render prompt template '%s': %s", self.name, e)
            raise PromptValidationError(
                f"Failed to render template '{self.name}' due to a configuration error."
            ) from e

        # Combine system prompt and human instruction for the final string sent to Ollama
        return f"System:\n{self.system_prompt}\n\nHuman:\n{rendered_human}"
