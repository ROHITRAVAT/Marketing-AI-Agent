"""Email service for sending application emails."""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import (
    FRONTEND_URL,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
)

logger = logging.getLogger(__name__)


def _build_password_reset_url(reset_token: str) -> str:
    """Build the frontend password reset URL."""

    return (
        f"{FRONTEND_URL.rstrip('/')}"
        f"/reset-password?token={reset_token}"
    )


def _build_password_reset_email(
    email: str,
    reset_token: str,
) -> EmailMessage:
    """Build the password reset email message."""

    reset_url = _build_password_reset_url(reset_token)

    message = EmailMessage()

    message["Subject"] = "Reset your Marketing AI Agent password"
    message["From"] = (
        f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    )
    message["To"] = email

    message.set_content(
        f"""
Hello,

We received a request to reset your Marketing AI Agent password.

Use the link below to reset your password:

{reset_url}

This password reset link will expire after 30 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
{SMTP_FROM_NAME}
""".strip()
    )

    message.add_alternative(
        f"""
<html>
    <body>
        <h2>Password Reset Request</h2>

        <p>Hello,</p>

        <p>
            We received a request to reset your
            Marketing AI Agent password.
        </p>

        <p>
            Click the button below to reset your password:
        </p>

        <p>
            <a
                href="{reset_url}"
                style="
                    display:inline-block;
                    padding:12px 20px;
                    background:#2563eb;
                    color:white;
                    text-decoration:none;
                    border-radius:6px;
                "
            >
                Reset Password
            </a>
        </p>

        <p>
            This password reset link will expire after 30 minutes.
        </p>

        <p>
            If you did not request a password reset,
            you can safely ignore this email.
        </p>

        <p>
            Regards,<br>
            {SMTP_FROM_NAME}
        </p>
    </body>
</html>
""".strip(),
        subtype="html",
    )

    return message


async def send_password_reset_email(
    email: str,
    reset_token: str,
) -> None:
    """Send a password reset email using SMTP."""

    if not SMTP_HOST:
        raise RuntimeError("SMTP_HOST is not configured")

    if not SMTP_USERNAME:
        raise RuntimeError("SMTP_USERNAME is not configured")

    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is not configured")

    if not SMTP_FROM_EMAIL:
        raise RuntimeError("SMTP_FROM_EMAIL is not configured")

    message = _build_password_reset_email(
        email,
        reset_token,
    )

    try:
        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30,
        ) as smtp:
            smtp.starttls()

            smtp.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            smtp.send_message(message)

        logger.info(
            "Password reset email sent to %s",
            email,
        )

    except Exception:
        logger.exception(
            "Failed to send password reset email to %s",
            email,
        )
        raise