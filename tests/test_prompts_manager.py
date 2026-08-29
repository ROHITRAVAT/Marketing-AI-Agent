import pytest
from app.prompts.manager import PromptManager
from app.prompts.base import PromptTemplate
from app.prompts.exceptions import PromptNotFoundError, PromptValidationError

@pytest.fixture
def manager():
    mgr = PromptManager()
    mgr.register_template(
        PromptTemplate(
            name="test_template",
            system_prompt="Test System.",
            human_template="Test {var1} and {var2}.",
            required_variables=["var1", "var2"]
        )
    )
    return mgr

def test_prompt_manager_valid_template(manager):
    """Test successful rendering of a valid registered template."""
    result = manager.get("test_template", var1="A", var2="B")
    assert "System:\nTest System." in result
    assert "Test A and B." in result

def test_prompt_manager_unknown_template(manager):
    """Test retrieving an unknown template raises PromptNotFoundError."""
    with pytest.raises(PromptNotFoundError, match="not found"):
        manager.get("unknown_template")

def test_prompt_manager_missing_variable(manager):
    """Test missing required variable raises PromptValidationError."""
    with pytest.raises(PromptValidationError, match="Missing required variables"):
        manager.get("test_template", var1="A")

def test_prompt_manager_invalid_input_type(manager):
    """Test None values for required variables raise PromptValidationError."""
    with pytest.raises(PromptValidationError, match="Missing required variables"):
        manager.get("test_template", var1="A", var2=None)

def test_prompt_manager_register_invalid_type():
    """Test registering an invalid object raises TypeError."""
    mgr = PromptManager()
    with pytest.raises(TypeError, match="instance of PromptTemplate"):
        mgr.register_template("Not a template")
