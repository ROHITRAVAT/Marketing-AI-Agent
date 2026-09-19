from datetime import datetime, date
from typing import Optional

from sqlalchemy import DateTime, Date, ForeignKey, Integer, String, JSON, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class SocialAnalytics(Base):
    """Normalized social media analytics data."""

    __tablename__ = "social_analytics"
    
    # We enforce a unique constraint so we can UPSERT metrics for the same post on the same day easily
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', 'external_post_id', 'metric_date', name='uix_analytics_post_date'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True
    )
    scheduled_post_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("scheduled_posts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    external_post_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # The date this metric snapshot represents (usually truncating to day level makes sense for history)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Normalized Metrics
    impressions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reach: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    engagement: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clicks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shares: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    saves: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    video_views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    followers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Raw payload from the provider for fields we haven't normalized
    provider_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign")
    scheduled_post: Mapped[Optional["ScheduledPost"]] = relationship("ScheduledPost")

    def __repr__(self) -> str:
        return f"<SocialAnalytics(id={self.id}, platform='{self.platform}', post='{self.external_post_id}')>"
