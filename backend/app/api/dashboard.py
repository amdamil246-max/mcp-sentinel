from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.invocation import ToolInvocation
from app.models.security import SecurityAlert
from app.models.approval import ApprovalRequest
from app.models.server import MCPServer

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    # 1. Total invocations
    total_invocations = db.query(func.count(ToolInvocation.id)).scalar() or 0

    # 2. Allowed vs Blocked vs Pending
    allowed_count = db.query(func.count(ToolInvocation.id)).filter(ToolInvocation.decision == "ALLOW").scalar() or 0
    blocked_count = db.query(func.count(ToolInvocation.id)).filter(ToolInvocation.decision == "BLOCK").scalar() or 0
    pending_approvals = db.query(func.count(ApprovalRequest.id)).filter(ApprovalRequest.status == "PENDING").scalar() or 0

    # 3. Critical & High Alerts
    critical_alerts = db.query(func.count(SecurityAlert.id)).filter(
        SecurityAlert.severity.in_(["Critical", "High"]), SecurityAlert.status == "NEW"
    ).scalar() or 0

    # 4. Average Risk Score
    avg_risk_score = round(db.query(func.avg(ToolInvocation.risk_score)).scalar() or 0.0, 1)

    # 5. MCP Server Status
    servers = db.query(MCPServer).all()
    server_status = {
        "total": len(servers),
        "healthy": sum(1 for s in servers if s.health_status == "healthy"),
        "degraded": sum(1 for s in servers if s.health_status == "degraded"),
        "offline": sum(1 for s in servers if s.health_status == "offline")
    }

    # 6. Risk Distribution
    risk_dist_rows = db.query(ToolInvocation.risk_classification, func.count(ToolInvocation.id)).group_by(ToolInvocation.risk_classification).all()
    risk_distribution_raw = dict(risk_dist_rows)
    risk_distribution = [
        {"name": "Low", "count": risk_distribution_raw.get("Low", 0), "color": "#10B981"},
        {"name": "Guarded", "count": risk_distribution_raw.get("Guarded", 0), "color": "#3B82F6"},
        {"name": "Medium", "count": risk_distribution_raw.get("Medium", 0), "color": "#F59E0B"},
        {"name": "High", "count": risk_distribution_raw.get("High", 0), "color": "#F97316"},
        {"name": "Critical", "count": risk_distribution_raw.get("Critical", 0), "color": "#EF4444"},
    ]

    # 7. Recent Security Events
    recent_invs = db.query(ToolInvocation).order_by(ToolInvocation.created_at.desc()).limit(10).all()
    recent_events = [
        {
            "id": inv.id,
            "tool_name": inv.tool_name,
            "server_id": inv.server_id,
            "risk_score": inv.risk_score,
            "risk_classification": inv.risk_classification,
            "decision": inv.decision,
            "status": inv.status,
            "timestamp": inv.created_at.isoformat()
        }
        for inv in recent_invs
    ]

    # 8. Top Risky Tools
    top_risky_rows = db.query(
        ToolInvocation.tool_name,
        func.avg(ToolInvocation.risk_score).label("avg_risk"),
        func.count(ToolInvocation.id).label("total")
    ).group_by(ToolInvocation.tool_name).order_by(func.avg(ToolInvocation.risk_score).desc()).limit(5).all()

    top_risky_tools = [
        {
            "tool_name": row[0],
            "average_risk": round(row[1], 1),
            "invocations": row[2]
        }
        for row in top_risky_rows
    ]

    return {
        "kpis": {
            "total_invocations": total_invocations,
            "allowed_operations": allowed_count,
            "blocked_operations": blocked_count,
            "pending_approvals": pending_approvals,
            "critical_alerts": critical_alerts,
            "average_risk_score": avg_risk_score,
            "server_status": server_status
        },
        "risk_distribution": risk_distribution,
        "recent_events": recent_events,
        "top_risky_tools": top_risky_tools
    }
