from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.core.security import compute_audit_hash

router = APIRouter(prefix="/audit", tags=["Audit & Forensics"])

@router.get("/logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    event_type: Optional[str] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if action:
        query = query.filter(AuditLog.action == action)
    if actor:
        query = query.filter(AuditLog.actor == actor)
    return query.limit(limit).all()

@router.get("/verify-chain")
def verify_audit_hash_chain(db: Session = Depends(get_db)) -> Dict[str, Any]:
    logs = db.query(AuditLog).order_by(AuditLog.created_at.asc()).all()

    if not logs:
        return {"status": "VERIFIED", "total_records": 0, "message": "No audit records to verify."}

    previous_hash = "GENESIS"
    for i, log in enumerate(logs):
        expected_hash = compute_audit_hash(
            log.previous_hash,
            log.event_type,
            log.actor,
            log.action,
            log.details,
            log.created_at
        )

        if log.previous_hash != previous_hash and i != 0:
            return {
                "status": "COMPROMISED",
                "compromised_at_index": i,
                "log_id": log.id,
                "reason": "Previous hash pointer mismatch.",
                "total_records_checked": i
            }

        if log.entry_hash != expected_hash:
            return {
                "status": "COMPROMISED",
                "compromised_at_index": i,
                "log_id": log.id,
                "reason": "Entry cryptographic signature does not match row contents.",
                "total_records_checked": i
            }

        previous_hash = log.entry_hash

    return {
        "status": "VERIFIED",
        "total_records": len(logs),
        "chain_head_hash": previous_hash,
        "message": "All audit log entries cryptographically verified. No tampering detected."
    }
