from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class MCPServerBase(BaseModel):
    name: str
    description: Optional[str] = None
    connection_type: str = "stdio"
    command: Optional[str] = None
    args: Optional[List[str]] = []
    env: Optional[Dict[str, str]] = {}
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = {}
    is_enabled: bool = True

class MCPServerCreate(MCPServerBase):
    id: str

class MCPServerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connection_type: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    is_enabled: Optional[bool] = None

class MCPServerResponse(MCPServerBase):
    id: str
    health_status: str
    last_connected_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tool_count: Optional[int] = 0

    class Config:
        from_attributes = True
