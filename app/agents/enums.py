from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class PlanStepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ToolExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class AgentStatus(str, Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    NEEDS_CLARIFICATION = "needs_clarification"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_MANUAL_ACTION = "requires_manual_action"