from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ApprovalStatus(str, Enum):
    """Available statuses for approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalRequest(Base):
    """Database model for storing human-in-the-loop approval requests."""

    __tablename__ = "approval_requests"

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

    thread_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    platform: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        String(50),
        default=ApprovalStatus.PENDING,
        server_default=ApprovalStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    reason: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rejected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        backref="approval_requests"
    )

    def __repr__(self) -> str:
        return (
            f"<ApprovalRequest("
            f"id={self.id}, "
            f"thread_id='{self.thread_id}', "
            f"action_type='{self.action_type}', "
            f"status='{self.status}'"
            f")>"
        )
