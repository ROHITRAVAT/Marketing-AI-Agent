from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ScheduledPost(Base):
    """Scheduled social/post entry for a campaign."""

    __tablename__ = "scheduled_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True, index=True
    )
    prompt_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("prompts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    approval_request_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Platform and account details
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Content
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_urls: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    
    # Scheduling info
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False, index=True)
    
    # Execution tracing
    thread_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Result
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    external_post_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_analytics_collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="scheduled_posts")
    prompt: Mapped[Optional["Prompt"]] = relationship("Prompt", back_populates="scheduled_posts")
    approval_request: Mapped[Optional["ApprovalRequest"]] = relationship("ApprovalRequest")

    def __repr__(self) -> str:
        return f"<ScheduledPost(id={self.id}, platform='{self.platform}', status='{self.status}')>"
