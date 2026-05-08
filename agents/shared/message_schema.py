from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
import json

# All 19 valid agent IDs — no agent outside this list
# may send or receive governed messages
VALID_AGENT_IDS = Literal[
    "ORCHESTRATOR_AGENT",
    "PO_AGENT_v1", "PO_AGENT_v2",
    "TL_AGENT_v1", "TL_AGENT_v2", "TL_AGENT_v3",
    "TL_AGENT_v4", "TL_AGENT_v5",
    "BE_AGENT_v1", "BE_AGENT_v2", "BE_AGENT_v3",
    "FE_AGENT_v1", "FE_AGENT_v2",
    "DO_AGENT_v1", "DO_AGENT_v2", "DO_AGENT_v3",
    "DO_AGENT_v4",
    "QA_AGENT_v1", "QA_AGENT_v2"
]

MESSAGE_TYPES = Literal[
    "TASK_ASSIGNMENT",
    "HANDOFF",
    "STATUS_UPDATE",
    "VALIDATION_RESULT",
    "BLOCKER_ALERT",
    "BLOCKER_RESOLVED",
    "COMPLETION_SIGNAL",
    "ACKNOWLEDGMENT",
    "ESCALATION_TRIGGERED",
    "RECOVERY_BUNDLE",
    "CIRCUIT_BREAKER_OPEN",
    "CIRCUIT_BREAKER_CLOSED",
    "EMERGENCY_HALT",
    "RESUME_BUILD"
]

PRIORITY_LEVELS = Literal["CRITICAL","HIGH","NORMAL","LOW"]

GOVERNANCE_RECORD_TYPES = Literal[
    "BUILD_INITIALIZED", "ORCHESTRATOR_READY",
    "WATCHDOG_START", "PHASE_OPEN", "PHASE_CLOSE",
    "TASK_START", "TASK_COMPLETE", "GATE_PASS",
    "HANDOFF_SENT", "ACKNOWLEDGMENT_RECEIVED",
    "BUILD_COMPLETE", "ORCHESTRATOR_SHUTDOWN",
    "RETRY_DISPATCHED", "CIRCUIT_BREAKER_OPEN",
    "CIRCUIT_BREAKER_HALF_OPEN", "CIRCUIT_BREAKER_CLOSED",
    "STALL_DETECTED", "BLOCKER_RAISED", "BLOCKER_RESOLVED",
    "ESCALATION_TRIGGERED", "BUILD_PAUSED", "BUILD_RESUMED",
    "BUILD_HALTED", "BUILD_ABANDONED", "RECOVERY_STARTED",
    "RECOVERY_FAILED", "STEP_27_OPEN",
    "LOG_COMPLETENESS_VERIFIED", "BUILD_CERTIFICATE_WRITTEN",
    "ARCHIVE_COMPLETE", "BACKFILL_RECORD",
    "UNAUTHORIZED_HALT_ATTEMPT", "HEARTBEAT"
]

class AgentMessage(BaseModel):
    model_config = {"extra": "forbid"}

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    message_type: MESSAGE_TYPES
    from_agent: VALID_AGENT_IDS
    to_agent: List[VALID_AGENT_IDS]
    build_id: str
    priority: PRIORITY_LEVELS = "NORMAL"
    requires_ack: bool = False
    ack_timeout_seconds: int = 300
    timestamp_utc: str = Field(
      default_factory=lambda: datetime.utcnow().isoformat()
    )
    payload: Dict[str, Any] = Field(default_factory=dict)
    context_for_next_agent: Optional[Dict[str, str]] = None

    @field_validator("to_agent")
    @classmethod
    def to_agent_not_empty(cls, v):
      if not v:
        raise ValueError("to_agent must not be empty")
      return v

class GovernanceRecord(BaseModel):
    model_config = {"extra": "forbid"}

    record_id: str = Field(default_factory=lambda: str(uuid4()))
    record_type: GOVERNANCE_RECORD_TYPES
    build_id: str
    agent_id: VALID_AGENT_IDS
    phase: Optional[str] = None
    step: Optional[str] = None
    timestamp_utc: str = Field(
      default_factory=lambda: datetime.utcnow().isoformat()
    )
    payload: Dict[str, Any] = Field(default_factory=dict)
    validation_rules_passed: Optional[List[str]] = None

    def to_jsonl_line(self) -> str:
      return self.model_dump_json() + "\n"
