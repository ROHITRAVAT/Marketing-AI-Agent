"""Centralized manager for prompt templates."""

import logging
from typing import Dict, Any
from app.prompts.base import PromptTemplate
from app.prompts.exceptions import PromptNotFoundError, PromptValidationError

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages registration, retrieval, and rendering of prompt templates."""

    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}

    def register_template(self, template: PromptTemplate) -> None:
        """Register a new prompt template."""
        if not isinstance(template, PromptTemplate):
            logger.error("Attempted to register invalid template object: %s", type(template))
            raise TypeError("template must be an instance of PromptTemplate")
        self._templates[template.name] = template

    def get(self, template_name: str, **kwargs: Any) -> str:
        """Retrieve and render a prompt template.
        
        Args:
            template_name: The name of the registered template.
            **kwargs: Variables to inject into the template.
            
        Returns:
            The rendered prompt string.
            
        Raises:
            PromptNotFoundError: If the template name is not registered.
            PromptValidationError: If rendering fails due to missing/invalid variables.
        """
        template = self._templates.get(template_name)
        if not template:
            logger.error("Prompt template '%s' was requested but not found in registry.", template_name)
            raise PromptNotFoundError(f"Prompt template '{template_name}' not found.")
            
        return template.render(**kwargs)

# Global singleton instance
prompt_manager = PromptManager()

# Import templates inside the file but after the instance to avoid circular logic
# if templates ever needed the manager (they don't, but it's safe here).
from app.prompts.content import marketing_content_template
from app.prompts.campaign import campaign_strategy_template
from app.prompts.seo import seo_optimization_template
from app.prompts.social_media import social_media_template

# Register the built-in templates automatically
prompt_manager.register_template(marketing_content_template)
prompt_manager.register_template(campaign_strategy_template)
prompt_manager.register_template(seo_optimization_template)
prompt_manager.register_template(social_media_template)
