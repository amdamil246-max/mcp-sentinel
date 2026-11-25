from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.invocation import ToolInvocation
from app.models.security import SecurityAnalysis
from app.schemas.invocation import (
    GatewayInvokeRequest,
    GatewayInvokeResponse,
    ToolInvocationResponse
)
from app.services.mcp_gateway.gateway import gateway

router = APIRouter(prefix="/gateway", tags=["MCP Gateway Execution"])

@router.post("/invoke", response_model=GatewayInvokeResponse)
def invoke_mcp_tool(
    request: GatewayInvokeRequest,
    db: Session = Depends(get_db)
):
    try:
        result = gateway.intercept_and_execute(
            db=db,
            server_id=request.server_id,
            tool_name=request.tool_name,
            arguments=request.arguments,
            session_id=request.session_id or "default-session",
            user_id="ai-agent"
        )
        return GatewayInvokeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway invocation error: {str(e)}")

@router.get("/invocations", response_model=List[ToolInvocationResponse])
def list_invocations(
    limit: int = Query(50, le=200),
    decision: Optional[str] = None,
    server_id: Optional[str] = None,
    tool_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ToolInvocation).order_by(ToolInvocation.created_at.desc())
    if decision:
        query = query.filter(ToolInvocation.decision == decision.upper())
    if server_id:
        query = query.filter(ToolInvocation.server_id == server_id)
    if tool_name:
        query = query.filter(ToolInvocation.tool_name == tool_name)
    return query.limit(limit).all()

@router.get("/invocations/{invocation_id}")
def get_invocation_details(
    invocation_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    invocation = db.query(ToolInvocation).filter(ToolInvocation.id == invocation_id).first()
    if not invocation:
        raise HTTPException(status_code=404, detail="Invocation not found.")

    analysis = db.query(SecurityAnalysis).filter(SecurityAnalysis.invocation_id == invocation_id).first()

    return {
        "invocation": ToolInvocationResponse.model_validate(invocation),
        "security_analysis": {
            "id": analysis.id,
            "risk_score": analysis.risk_score,
            "risk_classification": analysis.risk_classification,
            "triggered_rules": analysis.triggered_rules,
            "evidence": analysis.evidence,
            "reasoning": analysis.reasoning,
            "created_at": analysis.created_at.isoformat()
        } if analysis else None
    }
