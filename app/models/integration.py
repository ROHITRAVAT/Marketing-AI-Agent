from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class IntegrationConnection(Base):
    """Database model for storing OAuth connections to external platforms (e.g., LinkedIn)."""

    __tablename__ = "integration_connections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    provider_user_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    account_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    scopes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="integration_connections",
    )

    def __repr__(self) -> str:
        return (
            f"<IntegrationConnection("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"provider='{self.provider}'"
            f")>"
        )
