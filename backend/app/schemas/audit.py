from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: str
    event_type: str
    actor: str
    target_resource: str
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    previous_hash: Optional[str]
    entry_hash: str
    created_at: datetime

    class Config:
        from_attributes = True
