import pytest
from app.prompts.content import marketing_content_template
from app.prompts.exceptions import PromptValidationError

def test_marketing_content_template_render_success():
    """Test successful rendering of the content generation template."""
    result = marketing_content_template.render(
        product="Cloud Hosting",
        target_audience="Small Business Owners",
        platform="Email",
        campaign_goal="Increase signups",
        strategy="Highlight cost savings and ease of use."
    )
    
    assert "System:" in result
    assert "expert Marketing AI Copywriter" in result
    assert "Human:" in result
    assert "Product/Service: Cloud Hosting" in result
    assert "Platform: Email" in result
    assert "Highlight cost savings" in result

def test_marketing_content_template_missing_variables():
    """Test missing variables raise PromptValidationError."""
    with pytest.raises(PromptValidationError):
        marketing_content_template.render(
            product="Cloud Hosting",
            target_audience="Small Business Owners"
            # Missing platform, campaign_goal, strategy
        )
