from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta
from app.models.social_analytics import SocialAnalytics
from typing import Dict, Any

async def get_analytics_summary_for_agent(
    user_id: int,
    db: AsyncSession,
    days: int = 30
) -> Dict[str, Any]:
    """Retrieves an aggregated summary of analytics for the agent to answer questions."""
    start_date = date.today() - timedelta(days=days)
    
    stmt = select(
        SocialAnalytics.platform,
        func.count(SocialAnalytics.id).label("post_count"),
        func.sum(SocialAnalytics.impressions).label("total_impressions"),
        func.sum(SocialAnalytics.engagement).label("total_engagement")
    ).where(
        SocialAnalytics.user_id == user_id,
        SocialAnalytics.metric_date >= start_date
    ).group_by(SocialAnalytics.platform)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    summary = {
        "period_days": days,
        "platforms": []
    }
    
    overall_impressions = 0
    overall_engagement = 0
    
    for row in rows:
        p_imp = row.total_impressions or 0
        p_eng = row.total_engagement or 0
        summary["platforms"].append({
            "platform": row.platform,
            "posts_analyzed": row.post_count,
            "impressions": p_imp,
            "engagement": p_eng
        })
        overall_impressions += p_imp
        overall_engagement += p_eng
        
    summary["overall_impressions"] = overall_impressions
    summary["overall_engagement"] = overall_engagement
    
    return summary
