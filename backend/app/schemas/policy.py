from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class PolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    rule_type: str
    configuration: Dict[str, Any] = {}
    is_active: bool = True
    priority: int = 100

class PolicyCreate(PolicyBase):
    id: str

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    rule_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    change_summary: Optional[str] = "Policy updated"

class PolicyResponse(PolicyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
