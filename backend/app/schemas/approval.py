from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class ApprovalDecisionRequest(BaseModel):
    decision: str  # APPROVE or REJECT
    reason: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: str
    invocation_id: str
    tool_name: str
    server_name: str
    arguments_hash: str
    redacted_arguments: Dict[str, Any]
    risk_score: float
    reasons: List[str]
    requested_by: Optional[str]
    status: str
    decided_by: Optional[str]
    decision_reason: Optional[str]
    expires_at: datetime
    created_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True
