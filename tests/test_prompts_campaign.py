import pytest
from app.prompts.campaign import campaign_strategy_template
from app.prompts.exceptions import PromptValidationError

def test_campaign_strategy_template_render_success():
    """Test successful rendering of the campaign strategy template."""
    result = campaign_strategy_template.render(
        product="SaaS Tool",
        target_audience="Developers",
        platform="LinkedIn",
        campaign_goal="Lead Generation",
        analysis="User wants to target devs with a new CI/CD product."
    )
    
    assert "System:" in result
    assert "Senior Marketing Strategist" in result
    assert "Human:" in result
    assert "Product/Service: SaaS Tool" in result
    assert "Target Audience: Developers" in result
    assert "Preliminary Analysis:\nUser wants to target devs" in result

def test_campaign_strategy_template_missing_variables():
    """Test missing variables raise PromptValidationError."""
    with pytest.raises(PromptValidationError):
        campaign_strategy_template.render(
            product="SaaS Tool",
            target_audience="Developers",
            platform="LinkedIn"
            # Missing campaign_goal, analysis
        )
