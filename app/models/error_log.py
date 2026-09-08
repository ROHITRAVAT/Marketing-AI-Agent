from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database.base import Base

class AgentErrorLog(Base):
    __tablename__ = "agent_error_logs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(255), index=True, nullable=True)
    user_id = Column(Integer, index=True, nullable=True)
    node = Column(String(100), nullable=True)
    tool = Column(String(100), nullable=True)
    platform = Column(String(100), nullable=True)
    error_category = Column(String(100), nullable=False)
    error_code = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    retryable = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    resolution_status = Column(String(50), default="open") # open, retrying, recovered, failed, requires_manual_action
    metadata_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
