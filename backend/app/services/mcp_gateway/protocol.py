from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class MCPToolDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    inputSchema: Dict[str, Any] = {}

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Any
    method: str
    params: Optional[Dict[str, Any]] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Any
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
