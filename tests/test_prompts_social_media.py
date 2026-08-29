import pytest
from app.prompts.social_media import social_media_template
from app.prompts.exceptions import PromptValidationError

def test_social_media_template_render_success():
    """Test successful rendering of the social media template."""
    result = social_media_template.render(
        platform="LinkedIn",
        target_audience="B2B Executives",
        product="Enterprise CRM",
        campaign_goal="Book a Demo",
        generated_content="Our Enterprise CRM streamlines sales pipelines..."
    )
    
    assert "System:" in result
    assert "expert Social Media Manager" in result
    assert "Human:" in result
    assert "Platform: LinkedIn" in result
    assert "Target Audience: B2B Executives" in result
    assert "Source Content:\nOur Enterprise CRM" in result

def test_social_media_template_missing_variables():
    """Test missing variables raise PromptValidationError."""
    with pytest.raises(PromptValidationError):
        social_media_template.render(
            platform="LinkedIn",
            target_audience="B2B Executives",
            product="Enterprise CRM"
            # Missing campaign_goal, generated_content
        )
