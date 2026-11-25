from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.tool import RegisteredTool
from app.schemas.tool import RegisteredToolResponse, RegisteredToolUpdate
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/tools", tags=["Tools Registry"])

@router.get("", response_model=List[RegisteredToolResponse])
def list_tools(
    server_id: Optional[str] = None,
    trust_level: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RegisteredTool)
    if server_id:
        query = query.filter(RegisteredTool.server_id == server_id)
    if trust_level:
        query = query.filter(RegisteredTool.trust_level == trust_level)
    if is_enabled is not None:
        query = query.filter(RegisteredTool.is_enabled == is_enabled)
    return query.all()

@router.get("/{tool_id:path}", response_model=RegisteredToolResponse)
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    tool = db.query(RegisteredTool).filter(RegisteredTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found.")
    return tool

@router.patch("/{tool_id:path}/permissions", response_model=RegisteredToolResponse)
def update_tool_permissions(
    tool_id: str,
    tool_update: RegisteredToolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tool = db.query(RegisteredTool).filter(RegisteredTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found.")

    for field, val in tool_update.model_dump(exclude_unset=True).items():
        setattr(tool, field, val)

    tool.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tool)
    return tool
