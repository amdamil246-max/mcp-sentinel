from typing import Dict, Any, List, Optional
from app.services.security_engine.sensitive_data import SensitiveDataDetector
from app.config import settings

class AISecurityAnalyst:
    """
    AI-powered security advisor and incident explainer.
    Operates under a zero-trust model: redacts sensitive data, never executes tools,
    and never overrides deterministic security policies.
    """

    def __init__(self):
        self.secret_detector = SensitiveDataDetector()

    async def explain_decision(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        decision: str,
        risk_score: float,
        reasons: List[str],
        findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # Redact secrets before preparing prompt or explanation
        safe_args = self.secret_detector.redact(arguments)

        # Build comprehensive incident explanation
        summary = (
            f"Tool call '{tool_name}' evaluated with Risk Score {risk_score:.0f}/100 "
            f"resulting in enforcement decision: {decision}."
        )

        analysis_details = []
        for f in findings:
            rule = f.get("rule_name", "Unknown Rule")
            category = f.get("threat_category", "General")
            desc = f.get("description", "")
            analysis_details.append(f"• [{category}] {rule}: {desc}")

        remediation = []
        if decision == "BLOCK":
            remediation.append("Verify the AI agent's prompt boundary and check for compromised upstream context.")
            remediation.append("Restrict tool permissions or isolate execution within an unprivileged sandbox container.")
            remediation.append("Audit agent interaction logs for coordinated prompt injection attempts.")
        elif decision == "REQUIRE_APPROVAL":
            remediation.append("A security administrator should review the redacted parameters and intended outcome.")
            remediation.append("Confirm the legitimate business intent before granting temporary one-time execution.")
        else:
            remediation.append("Normal baseline operation. Continue standard continuous auditing.")

        return {
            "summary": summary,
            "decision": decision,
            "risk_score": risk_score,
            "threat_breakdown": analysis_details if analysis_details else ["No anomalous security signatures found."],
            "root_cause": reasons[0] if reasons else "Policy baseline evaluation.",
            "remediation_recommendations": remediation,
            "ai_disclaimer": "AI Security Analyst output is advisory only. Enforcement is governed by deterministic policies."
        }

    async def generate_incident_report(
        self,
        alert_title: str,
        severity: str,
        threat_category: str,
        evidence: Dict[str, Any],
        affected_tool: str
    ) -> Dict[str, Any]:
        return {
            "report_id": f"REP-{hash(alert_title) % 100000:05d}",
            "title": f"Security Incident Report: {alert_title}",
            "severity": severity,
            "threat_category": threat_category,
            "affected_resource": affected_tool,
            "executive_summary": (
                f"An automated security interception occurred targeting '{affected_tool}'. "
                f"The attack pattern was classified as '{threat_category}' with '{severity}' severity. "
                f"MCP Sentinel successfully intercepted and isolated the event."
            ),
            "technical_indicators": evidence,
            "recommended_actions": [
                "Inspect the agent's recent context window for malicious indirect injection.",
                "Review server-side tool permission thresholds.",
                "Ensure network egress from the tool container is strictly segmented."
            ]
        }

ai_analyst = AISecurityAnalyst()
