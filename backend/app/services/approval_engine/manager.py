import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.approval import ApprovalRequest
from app.models.invocation import ToolInvocation
from app.core.security import compute_arguments_hash
from app.services.security_engine.sensitive_data import SensitiveDataDetector
from app.config import settings
from app.core.events import broadcaster

class ApprovalEngine:
    """
    Manages human approval lifecycle with cryptographic argument validation,
    time-based expiration, and status transitions.
    """

    def __init__(self):
        self.secret_detector = SensitiveDataDetector()

    def create_request(
        self,
        db: Session,
        invocation_id: str,
        tool_name: str,
        server_name: str,
        arguments: Dict[str, Any],
        risk_score: float,
        reasons: List[str],
        requested_by: Optional[str] = "agent-session",
        expiration_seconds: Optional[int] = None
    ) -> ApprovalRequest:
        exp_sec = expiration_seconds or settings.GATEWAY_APPROVAL_EXPIRATION_SECONDS
        expires_at = datetime.utcnow() + timedelta(seconds=exp_sec)
        
        args_hash = compute_arguments_hash(arguments)
        redacted_args = self.secret_detector.redact(arguments)

        approval = ApprovalRequest(
            id=f"appr-{uuid.uuid4().hex[:12]}",
            invocation_id=invocation_id,
            tool_name=tool_name,
            server_name=server_name,
            arguments_hash=args_hash,
            redacted_arguments=redacted_args,
            risk_score=risk_score,
            reasons=reasons,
            requested_by=requested_by,
            status="PENDING",
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        return approval

    def evaluate_decision(
        self,
        db: Session,
        approval_id: str,
        decision: str,  # "APPROVE" or "REJECT"
        decided_by: str,
        reason: Optional[str] = None
    ) -> ApprovalRequest:
        approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()

        if not approval:
            raise ValueError(f"Approval request '{approval_id}' not found.")

        if approval.status != "PENDING":
            raise ValueError(f"Approval request '{approval_id}' is already {approval.status}.")

        if datetime.utcnow() > approval.expires_at:
            approval.status = "EXPIRED"
            db.commit()
            raise ValueError(f"Approval request '{approval_id}' has expired.")

        new_status = "APPROVED" if decision.upper() == "APPROVE" else "REJECTED"
        approval.status = new_status
        approval.decided_by = decided_by
        approval.decision_reason = reason or f"Decided as {new_status} by {decided_by}"
        approval.decided_at = datetime.utcnow()

        invocation = db.query(ToolInvocation).filter(ToolInvocation.id == approval.invocation_id).first()
        if invocation:
            invocation.approval_status = new_status
            if new_status == "REJECTED":
                invocation.status = "blocked"
                invocation.decision = "BLOCK"

        db.commit()
        db.refresh(approval)
        return approval

    def verify_arguments_integrity(self, approval: ApprovalRequest, execution_arguments: Dict[str, Any]) -> bool:
        """Ensures arguments have not been altered or tampered with since approval was requested."""
        current_hash = compute_arguments_hash(execution_arguments)
        return current_hash == approval.arguments_hash

approval_engine = ApprovalEngine()
