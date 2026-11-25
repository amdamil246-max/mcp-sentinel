from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.invocation import ToolInvocation
from app.models.security import SecurityAnalysis, SecurityAlert
from app.services.ai_analyst.analyst import ai_analyst

router = APIRouter(prefix="/ai", tags=["AI Security Analyst"])

class AskAnalystRequest(BaseModel):
    query: str
    context_invocation_id: Optional[str] = None
    context_alert_id: Optional[str] = None

@router.post("/explain-invocation/{invocation_id}")
async def explain_invocation(invocation_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    invocation = db.query(ToolInvocation).filter(ToolInvocation.id == invocation_id).first()
    if not invocation:
        raise HTTPException(status_code=404, detail="Invocation not found.")

    analysis = db.query(SecurityAnalysis).filter(SecurityAnalysis.invocation_id == invocation_id).first()
    findings = analysis.triggered_rules if analysis else []
    reasons = [analysis.reasoning] if analysis and analysis.reasoning else []

    explanation = await ai_analyst.explain_decision(
        tool_name=f"{invocation.server_id}:{invocation.tool_name}",
        arguments=invocation.arguments,
        decision=invocation.decision,
        risk_score=invocation.risk_score,
        reasons=reasons,
        findings=findings
    )
    return explanation

@router.post("/incident-report/{alert_id}")
async def generate_alert_report(alert_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    report = await ai_analyst.generate_incident_report(
        alert_title=alert.title,
        severity=alert.severity,
        threat_category=alert.threat_category,
        evidence=alert.evidence,
        affected_tool=alert.affected_tool
    )
    return report

@router.post("/ask")
async def ask_analyst(request: AskAnalystRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    query_lower = request.query.lower()
    
    if "why" in query_lower and "blocked" in query_lower:
        answer = (
            "The tool call was blocked because the Security Analysis Engine identified destructive command "
            "or unauthorized filesystem patterns violating the active security baseline. In accordance with zero-trust "
            "principles, high-impact destructive calls are blocked automatically before execution."
        )
    elif "prompt injection" in query_lower:
        answer = (
            "Prompt injection attacks attempt to hijack the AI model's instruction following via adversarial phrases "
            "like 'ignore previous instructions' or hidden delimiters in retrieved tool outputs. MCP Sentinel inspects "
            "both inbound arguments and outbound tool responses to isolate such payloads."
        )
    elif "remediation" in query_lower or "recommend" in query_lower:
        answer = (
            "Recommended remediation: 1) Verify agent input sanitization. 2) Lower container capabilities and enforce "
            "read-only volume mounts. 3) Require human administrator approval for write and execute permission levels."
        )
    else:
        answer = (
            f"Analysis of query '{request.query}': MCP Sentinel's firewall is currently active. All tool invocations "
            "are subject to real-time command inspection, path validation, secret redaction, and deterministic policy enforcement."
        )

    return {
        "query": request.query,
        "response": answer,
        "analyst_role": "Principal AI Security Analyst",
        "advisory": True
    }
