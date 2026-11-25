from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.approval import ApprovalRequest
from app.schemas.approval import ApprovalResponse, ApprovalDecisionRequest
from app.services.approval_engine.manager import approval_engine
from app.services.mcp_gateway.gateway import gateway
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/approvals", tags=["Human Approvals"])

@router.get("", response_model=List[ApprovalResponse])
def list_approvals(
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())
    if status:
        query = query.filter(ApprovalRequest.status == status.upper())
    return query.limit(limit).all()

@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(approval_id: str, db: Session = Depends(get_db)):
    appr = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not appr:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    return appr

@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
def approve_request(
    approval_id: str,
    decision_in: Optional[ApprovalDecisionRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        appr = approval_engine.evaluate_decision(
            db=db,
            approval_id=approval_id,
            decision="APPROVE",
            decided_by=current_user.username,
            reason=decision_in.reason if decision_in else "Approved by administrator"
        )
        return appr
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
def reject_request(
    approval_id: str,
    decision_in: Optional[ApprovalDecisionRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        appr = approval_engine.evaluate_decision(
            db=db,
            approval_id=approval_id,
            decision="REJECT",
            decided_by=current_user.username,
            reason=decision_in.reason if decision_in else "Rejected by administrator"
        )
        return appr
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{approval_id}/execute")
def execute_approved(
    approval_id: str,
    execution_arguments: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        res = gateway.execute_approved_invocation(
            db=db,
            approval_id=approval_id,
            execution_arguments=execution_arguments
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
