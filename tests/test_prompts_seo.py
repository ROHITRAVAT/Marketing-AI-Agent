import pytest
from app.prompts.seo import seo_optimization_template
from app.prompts.exceptions import PromptValidationError

def test_seo_optimization_template_render_success():
    """Test successful rendering of the SEO optimization template."""
    result = seo_optimization_template.render(
        product="Eco-Friendly Water Bottle",
        target_audience="Environmentally conscious millennials",
        generated_content="Stay hydrated while saving the planet with our new reusable bottle..."
    )
    
    assert "System:" in result
    assert "expert SEO Specialist" in result
    assert "Human:" in result
    assert "Product/Service: Eco-Friendly Water Bottle" in result
    assert "Marketing Content:\nStay hydrated" in result

def test_seo_optimization_template_missing_variables():
    """Test missing variables raise PromptValidationError."""
    with pytest.raises(PromptValidationError):
        seo_optimization_template.render(
            product="Eco-Friendly Water Bottle",
            target_audience="Environmentally conscious millennials"
            # Missing generated_content
        )
