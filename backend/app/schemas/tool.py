from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class RegisteredToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = {}
    permission_level: str = "execute"
    trust_level: str = "untrusted"
    is_enabled: bool = True
    requires_approval: bool = False

class RegisteredToolCreate(RegisteredToolBase):
    id: str
    server_id: str

class RegisteredToolUpdate(BaseModel):
    description: Optional[str] = None
    permission_level: Optional[str] = None
    trust_level: Optional[str] = None
    is_enabled: Optional[bool] = None
    requires_approval: Optional[bool] = None

class RegisteredToolResponse(RegisteredToolBase):
    id: str
    server_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
