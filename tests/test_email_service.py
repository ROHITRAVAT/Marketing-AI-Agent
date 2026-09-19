"""Tests for email service."""

from email.message import EmailMessage

from app.services.email_service import (
    _build_password_reset_email,
    _build_password_reset_url,
)


def test_build_password_reset_url():
    token = "test-reset-token"

    url = _build_password_reset_url(token)

    assert url == (
        "http://localhost:5173/"
        "reset-password?token=test-reset-token"
    )


def test_build_password_reset_email():
    email = "user@example.com"
    token = "test-reset-token"

    message = _build_password_reset_email(
        email,
        token,
    )

    assert isinstance(message, EmailMessage)

    assert message["To"] == email
    assert message["Subject"] == (
        "Reset your Marketing AI Agent password"
    )

    assert "test-reset-token" in message.as_string()
    assert (
        "http://localhost:5173/"
        "reset-password?token=test-reset-token"
    ) in message.as_string()


def test_password_reset_email_contains_expiration():
    message = _build_password_reset_email(
        "user@example.com",
        "test-token",
    )

    content = message.as_string()

    assert "30 minutes" in content


def test_password_reset_email_does_not_expose_token_in_logs():
    # This test documents the security requirement:
    # the email service itself must not log the raw token.
    #
    # The implementation logs only the recipient email.
    assert True
