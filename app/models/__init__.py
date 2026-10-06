"""models package — import model classes to ensure they are registered
with SQLAlchemy metadata when modules import `app.models`.
"""

from .user import User
from .campaign import Campaign
from .prompt import Prompt
from .scheduled_post import ScheduledPost
from .agent_log import AgentLog
from .error_log import AgentErrorLog
from .approval import ApprovalRequest
from .password_reset_token import PasswordResetToken
from .integration import IntegrationConnection
from .social_analytics import SocialAnalytics
from .agent_job import AgentJob

# For Alembic to detect these models, make sure they are imported above
# and exposed in the __all__ list below if you use wildcard imports elsewhere.

__all__ = [
    "User",
    "Campaign",
    "Prompt",
    "ScheduledPost",
    "AgentLog",
    "AgentErrorLog",
    "ApprovalRequest",
    "PasswordResetToken",
    "IntegrationConnection",
    "SocialAnalytics",
    "AgentJob",
]
