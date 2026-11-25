from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class SecurityAnalysisResponse(BaseModel):
    id: str
    invocation_id: str
    risk_score: float
    risk_classification: str
    triggered_rules: List[Dict[str, Any]]
    evidence: Dict[str, Any]
    reasoning: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SecurityAlertResponse(BaseModel):
    id: str
    invocation_id: Optional[str]
    threat_category: str
    severity: str
    title: str
    description: str
    evidence: Dict[str, Any]
    affected_tool: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class SecurityAlertUpdate(BaseModel):
    status: str  # NEW, INVESTIGATING, RESOLVED, DISMISSED
