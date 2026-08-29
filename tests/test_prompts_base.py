import pytest
from app.prompts.base import PromptTemplate
from app.prompts.exceptions import PromptValidationError

def test_prompt_template_render_success():
    """Test successful rendering of a prompt template."""
    template = PromptTemplate(
        name="test_template",
        system_prompt="You are a helpful assistant.",
        human_template="My name is {name} and I am {age} years old.",
        required_variables=["name", "age"]
    )
    
    result = template.render(name="Alice", age=30)
    
    expected = (
        "System:\nYou are a helpful assistant.\n\n"
        "Human:\nMy name is Alice and I am 30 years old."
    )
    assert result == expected

def test_prompt_template_missing_required_variable():
    """Test missing required variable raises PromptValidationError."""
    template = PromptTemplate(
        name="test_template",
        system_prompt="You are a helpful assistant.",
        human_template="My name is {name}.",
        required_variables=["name"]
    )
    
    with pytest.raises(PromptValidationError, match="Missing required variables"):
        template.render()

def test_prompt_template_null_required_variable():
    """Test required variable with None value raises PromptValidationError."""
    template = PromptTemplate(
        name="test_template",
        system_prompt="You are a helpful assistant.",
        human_template="My name is {name}.",
        required_variables=["name"]
    )
    
    with pytest.raises(PromptValidationError, match="Missing required variables"):
        template.render(name=None)

def test_prompt_template_empty_string_variable():
    """Test required variable with empty string raises PromptValidationError."""
    template = PromptTemplate(
        name="test_template",
        system_prompt="You are a helpful assistant.",
        human_template="My name is {name}.",
        required_variables=["name"]
    )
    
    with pytest.raises(PromptValidationError, match="Missing required variables"):
        template.render(name="   ")

def test_prompt_template_extra_kwargs_ignored():
    """Test that extra kwargs not in the human template are safely ignored."""
    template = PromptTemplate(
        name="test_template",
        system_prompt="You are a helpful assistant.",
        human_template="My name is {name}.",
        required_variables=["name"]
    )
    
    result = template.render(name="Alice", extra="ignored")
    assert "Alice" in result
    assert "ignored" not in result

def test_prompt_template_key_error_fallback():
    """Test that a variable in the format string but not in required_variables raises PromptValidationError."""
    template = PromptTemplate(
        name="test_template",
        system_prompt="You are a helpful assistant.",
        human_template="My name is {name} and I live in {city}.",
        required_variables=["name"]
    )
    
    with pytest.raises(PromptValidationError, match="expects variable 'city'"):
        template.render(name="Alice")

def test_prompt_template_malformed_configuration():
    """Test that malformed format strings trigger a generic validation error."""
    template = PromptTemplate(
        name="test_template",
        system_prompt="You are a helpful assistant.",
        human_template="My name is {name} and this is invalid {.",
        required_variables=["name"]
    )
    
    with pytest.raises(PromptValidationError, match="due to a configuration error"):
        template.render(name="Alice")
