from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserRole(str, Enum):
    """Available roles for application users."""

    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
    String(20),
    default=UserRole.USER,
    server_default=UserRole.USER.value,
    nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
    Boolean,
    default=True,
    server_default="true",
    nullable=False,
    )

    is_superuser: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    server_default="false",
    nullable=False,
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
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    prompts: Mapped[List["Prompt"]] = relationship(
        "Prompt",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    password_reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<User("
            f"id={self.id}, "
            f"email='{self.email}', "
            f"role='{self.role}', "
            f"is_active={self.is_active}"
            f")>"
        )