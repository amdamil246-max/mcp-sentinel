from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class ToolInvocationCreate(BaseModel):
    server_id: str
    tool_name: str
    arguments: Dict[str, Any] = {}
    session_id: Optional[str] = "default-session"
    user_id: Optional[str] = "agent-user"

class GatewayInvokeRequest(BaseModel):
    server_id: str
    tool_name: str
    arguments: Dict[str, Any] = {}
    session_id: Optional[str] = "session-1"

class GatewayInvokeResponse(BaseModel):
    invocation_id: str
    decision: str  # ALLOW, BLOCK, REQUIRE_APPROVAL
    risk_score: float
    risk_classification: str
    status: str
    reasons: List[str] = []
    approval_id: Optional[str] = None
    result: Optional[Any] = None
    execution_duration_ms: float = 0.0

class ToolInvocationResponse(BaseModel):
    id: str
    session_id: Optional[str]
    user_id: Optional[str]
    server_id: str
    tool_name: str
    arguments: Dict[str, Any]
    status: str
    risk_score: float
    risk_classification: str
    decision: str
    approval_status: str
    execution_status: str
    response_data: Optional[Any]
    execution_duration_ms: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
