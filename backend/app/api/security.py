from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.security import SecurityAlert
from app.schemas.security import SecurityAlertResponse, SecurityAlertUpdate
from app.services.security_engine import security_engine
from app.services.risk_engine.scorer import risk_engine
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/security", tags=["Security & Alerts"])

@router.get("/alerts", response_model=List[SecurityAlertResponse])
def list_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    threat_category: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(SecurityAlert).order_by(SecurityAlert.created_at.desc())
    if severity:
        query = query.filter(SecurityAlert.severity == severity)
    if status:
        query = query.filter(SecurityAlert.status == status.upper())
    if threat_category:
        query = query.filter(SecurityAlert.threat_category == threat_category)
    return query.limit(limit).all()

@router.get("/alerts/{alert_id}", response_model=SecurityAlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Security alert not found.")
    return alert

@router.patch("/alerts/{alert_id}", response_model=SecurityAlertResponse)
def update_alert_status(
    alert_id: str,
    update_data: SecurityAlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Security alert not found.")

    alert.status = update_data.status.upper()
    if alert.status in ("RESOLVED", "DISMISSED"):
        alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert

@router.post("/scan")
def scan_payload(
    payload: Dict[str, Any],
    tool_name: Optional[str] = "custom_tool"
) -> Dict[str, Any]:
    sec_res = security_engine.inspect_request(
        server_id="manual-scanner",
        tool_name=tool_name,
        arguments=payload
    )
    risk_assessment = risk_engine.calculate_risk(sec_res.findings)
    return {
        "max_risk_score": risk_assessment.score,
        "classification": risk_assessment.classification,
        "findings": sec_res.findings,
        "evidence": sec_res.evidence,
        "recommended_action": risk_assessment.recommended_action
    }
