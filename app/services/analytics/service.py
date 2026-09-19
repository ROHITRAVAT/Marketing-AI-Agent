from datetime import datetime, date, timezone
from typing import Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.scheduled_post import ScheduledPost
from app.models.social_analytics import SocialAnalytics
from app.core.oauth.manager import TokenManager
from app.core.errors import SocialMediaAPIError

from app.services.analytics.providers.twitter_provider import TwitterAnalyticsProvider
from app.services.analytics.providers.linkedin_provider import LinkedInAnalyticsProvider
from app.services.analytics.providers.facebook_provider import FacebookAnalyticsProvider
from app.services.analytics.providers.instagram_provider import InstagramAnalyticsProvider

logger = logging.getLogger(__name__)

class AnalyticsService:
    PROVIDERS = {
        "twitter": TwitterAnalyticsProvider(),
        "linkedin": LinkedInAnalyticsProvider(),
        "facebook": FacebookAnalyticsProvider(),
        "instagram": InstagramAnalyticsProvider(),
    }

    @classmethod
    async def collect_post_analytics(cls, post: ScheduledPost, db: AsyncSession) -> Optional[SocialAnalytics]:
        """
        Fetch analytics for a single ScheduledPost and upsert into the SocialAnalytics table.
        """
        if not post.external_post_id:
            logger.warning(f"Cannot fetch analytics for post {post.id} without external_post_id")
            return None

        provider = cls.PROVIDERS.get(post.platform.lower())
        if not provider:
            logger.warning(f"No analytics provider found for platform: {post.platform}")
            return None

        try:
            # 1. Get a valid access token
            access_token = await TokenManager.get_valid_access_token(post.user_id, post.platform.lower(), db)
            
            # 2. Fetch metrics
            metrics = await provider.get_post_metrics(
                post_id=post.external_post_id,
                access_token=access_token,
                account_id=post.account_id
            )
            
            # 3. Prepare data for upsert
            today = datetime.now(timezone.utc).date()
            
            stmt = insert(SocialAnalytics).values(
                user_id=post.user_id,
                campaign_id=post.campaign_id,
                scheduled_post_id=post.id,
                external_post_id=post.external_post_id,
                platform=post.platform.lower(),
                metric_date=today,
                impressions=metrics.get("impressions"),
                reach=metrics.get("reach"),
                engagement=metrics.get("engagement"),
                clicks=metrics.get("clicks"),
                likes=metrics.get("likes"),
                comments=metrics.get("comments"),
                shares=metrics.get("shares"),
                saves=metrics.get("saves"),
                video_views=metrics.get("video_views"),
                followers=metrics.get("followers"),
                provider_metrics=metrics.get("provider_metrics"),
                collected_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # On conflict on (user_id, platform, external_post_id, metric_date), update
            update_dict = {
                "impressions": stmt.excluded.impressions,
                "reach": stmt.excluded.reach,
                "engagement": stmt.excluded.engagement,
                "clicks": stmt.excluded.clicks,
                "likes": stmt.excluded.likes,
                "comments": stmt.excluded.comments,
                "shares": stmt.excluded.shares,
                "saves": stmt.excluded.saves,
                "video_views": stmt.excluded.video_views,
                "followers": stmt.excluded.followers,
                "provider_metrics": stmt.excluded.provider_metrics,
                "collected_at": stmt.excluded.collected_at,
                "updated_at": stmt.excluded.updated_at,
            }
            
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['user_id', 'platform', 'external_post_id', 'metric_date'],
                set_=update_dict
            ).returning(SocialAnalytics)
            
            result = await db.execute(upsert_stmt)
            analytics_record = result.scalar_one_or_none()
            
            # Update the post's last collected timestamp
            post.last_analytics_collected_at = datetime.now(timezone.utc)
            await db.commit()
            
            return analytics_record
            
        except SocialMediaAPIError as e:
            logger.error(f"API error fetching analytics for post {post.id} ({post.platform}): {e.message}")
            # If token expired or rate limited, don't update last_analytics_collected_at so it retries soon
        except Exception as e:
            logger.exception(f"Unexpected error fetching analytics for post {post.id}: {str(e)}")
            
        return None
