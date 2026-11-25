from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.server import MCPServer
from app.models.tool import RegisteredTool
from app.schemas.server import MCPServerCreate, MCPServerUpdate, MCPServerResponse
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/mcp/servers", tags=["MCP Servers"])

@router.get("", response_model=List[MCPServerResponse])
def list_servers(db: Session = Depends(get_db)):
    servers = db.query(MCPServer).all()
    response = []
    for srv in servers:
        count = db.query(func.count(RegisteredTool.id)).filter(RegisteredTool.server_id == srv.id).scalar() or 0
        srv_data = MCPServerResponse.model_validate(srv)
        srv_data.tool_count = count
        response.append(srv_data)
    return response

@router.post("", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
def create_server(
    server_in: MCPServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exists = db.query(MCPServer).filter(MCPServer.id == server_in.id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Server with this ID already exists.")

    new_server = MCPServer(
        id=server_in.id,
        name=server_in.name,
        description=server_in.description,
        connection_type=server_in.connection_type,
        command=server_in.command,
        args=server_in.args or [],
        env=server_in.env or {},
        url=server_in.url,
        headers=server_in.headers or {},
        is_enabled=server_in.is_enabled,
        health_status="healthy",
        last_connected_at=datetime.utcnow()
    )
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    
    resp = MCPServerResponse.model_validate(new_server)
    resp.tool_count = 0
    return resp

@router.get("/{server_id}", response_model=MCPServerResponse)
def get_server(server_id: str, db: Session = Depends(get_db)):
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")
    
    count = db.query(func.count(RegisteredTool.id)).filter(RegisteredTool.server_id == server.id).scalar() or 0
    resp = MCPServerResponse.model_validate(server)
    resp.tool_count = count
    return resp

@router.patch("/{server_id}", response_model=MCPServerResponse)
def update_server(
    server_id: str,
    server_update: MCPServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    for field, val in server_update.model_dump(exclude_unset=True).items():
        setattr(server, field, val)

    server.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(server)
    return MCPServerResponse.model_validate(server)

@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_server(
    server_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    db.delete(server)
    db.commit()
    return None
