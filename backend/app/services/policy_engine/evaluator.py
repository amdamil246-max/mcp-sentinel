from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.risk_engine.scorer import RiskAssessment
from app.config import settings

class PolicyDecision(BaseModel):
    decision: str  # ALLOW, BLOCK, REQUIRE_APPROVAL
    reason: str
    risk_score: float
    risk_classification: str
    reasons_list: List[str]
    mandatory_block: bool = False
    requires_approval: bool = False

class PolicyEngine:
    """
    Evaluates risk assessments and operational policies to produce
    deterministic enforcement decisions (ALLOW, BLOCK, REQUIRE_APPROVAL).
    """

    def evaluate(
        self,
        risk_assessment: RiskAssessment,
        is_tool_enabled: bool = True,
        is_server_enabled: bool = True,
        explicit_approval_required: bool = False,
        custom_policies: Optional[List[Dict[str, Any]]] = None
    ) -> PolicyDecision:
        reasons_list: List[str] = []

        # 1. Server or Tool Disabled Checks
        if not is_server_enabled:
            return PolicyDecision(
                decision="BLOCK",
                reason="The destination MCP Server is currently disabled or offline.",
                risk_score=100.0,
                risk_classification="Critical",
                reasons_list=["Destination MCP Server disabled by administrator"],
                mandatory_block=True
            )

        if not is_tool_enabled:
            return PolicyDecision(
                decision="BLOCK",
                reason="The requested tool is disabled by administrator policy.",
                risk_score=100.0,
                risk_classification="Critical",
                reasons_list=["Tool disabled by administrator policy"],
                mandatory_block=True
            )

        # 2. Check for Mandatory Critical Violations
        # High-risk destructive commands, prompt injections, or critical file traversals
        for finding in risk_assessment.triggered_rules:
            severity = finding.get("severity")
            rule_name = finding.get("rule_name", "Security Violation")
            rule_score = finding.get("risk_score", 0.0)

            if severity == "Critical" or rule_score >= settings.AUTO_BLOCK_SCORE_THRESHOLD:
                reasons_list.append(f"MANDATORY POLICY BLOCK: {rule_name} (Score: {rule_score:.0f})")

        if reasons_list:
            return PolicyDecision(
                decision="BLOCK",
                reason="Operation blocked due to mandatory security policy violation.",
                risk_score=risk_assessment.score,
                risk_classification="Critical",
                reasons_list=reasons_list,
                mandatory_block=True
            )

        # 3. Check for Human Approval Requirement
        if explicit_approval_required or risk_assessment.recommended_action == "REQUIRE_APPROVAL":
            approval_reasons = [
                f"Risk score ({risk_assessment.score:.0f}) meets or exceeds human approval threshold ({settings.APPROVAL_REQUIRED_SCORE_THRESHOLD})"
            ]
            for finding in risk_assessment.triggered_rules:
                approval_reasons.append(f"Threat signal: {finding.get('rule_name')}")

            return PolicyDecision(
                decision="REQUIRE_APPROVAL",
                reason="Operation requires authorized human administrator approval prior to execution.",
                risk_score=risk_assessment.score,
                risk_classification=risk_assessment.classification,
                reasons_list=approval_reasons,
                requires_approval=True
            )

        # 4. Check for High Score Block
        if risk_assessment.score >= settings.AUTO_BLOCK_SCORE_THRESHOLD:
            return PolicyDecision(
                decision="BLOCK",
                reason=f"Risk score {risk_assessment.score:.0f} exceeds auto-block threshold ({settings.AUTO_BLOCK_SCORE_THRESHOLD}).",
                risk_score=risk_assessment.score,
                risk_classification=risk_assessment.classification,
                reasons_list=[f"Risk score {risk_assessment.score:.0f} exceeds auto-block threshold"],
                mandatory_block=True
            )

        # 5. Allow
        return PolicyDecision(
            decision="ALLOW",
            reason="Tool invocation conforms to active security policies.",
            risk_score=risk_assessment.score,
            risk_classification=risk_assessment.classification,
            reasons_list=["Operation permitted under active security baseline"]
        )

policy_engine = PolicyEngine()
