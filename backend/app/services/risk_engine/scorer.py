from typing import Dict, Any, List, Tuple
from pydantic import BaseModel
from app.config import settings

class RiskAssessment(BaseModel):
    score: float
    classification: str  # Low, Guarded, Medium, High, Critical
    triggered_rules: List[Dict[str, Any]]
    evidence: Dict[str, Any]
    reasoning: str
    recommended_action: str  # ALLOW, REQUIRE_APPROVAL, BLOCK

class RiskScoringEngine:
    """
    Computes explainable, deterministic risk scores between 0 and 100
    combining security findings, tool permissions, and destination trust.
    """

    TOOL_PERMISSION_BASE_SCORES = {
        "read": 5.0,
        "list": 5.0,
        "write": 25.0,
        "create": 25.0,
        "execute": 45.0,
        "admin": 65.0,
    }

    TRUST_LEVEL_MODIFIERS = {
        "trusted": -10.0,
        "monitored": 0.0,
        "untrusted": 15.0,
        "blocked": 100.0,
    }

    def calculate_risk(
        self,
        security_findings: List[Dict[str, Any]],
        permission_level: str = "execute",
        trust_level: str = "untrusted",
        is_sensitive_tool: bool = False,
        requires_manual_approval: bool = False
    ) -> RiskAssessment:
        triggered_rules: List[Dict[str, Any]] = list(security_findings)
        reasons: List[str] = []

        # 1. Base score from permission level
        base_score = self.TOOL_PERMISSION_BASE_SCORES.get(permission_level.lower(), 25.0)
        reasons.append(f"Base tool capability '{permission_level}' (+{base_score:.0f})")

        # 2. Server/Tool Trust Level modifier
        trust_mod = self.TRUST_LEVEL_MODIFIERS.get(trust_level.lower(), 15.0)
        if trust_mod != 0:
            reasons.append(f"Trust tier '{trust_level}' ({trust_mod:+.0f})")

        # 3. Sensitive Tool flag
        sensitive_mod = 20.0 if is_sensitive_tool else 0.0
        if sensitive_mod > 0:
            reasons.append("Tool designated as high-impact sensitive (+20)")

        # 4. Security Findings Impact
        finding_score = 0.0
        if security_findings:
            # Highest individual finding has dominant weight
            max_finding = max(f.get("risk_score", 0.0) for f in security_findings)
            # Secondary findings contribute diminishing weights
            additional = sum(f.get("risk_score", 0.0) * 0.1 for f in security_findings) - (max_finding * 0.1)
            finding_score = max_finding + max(0.0, additional)
            reasons.append(f"Security detection engine identified {len(security_findings)} threat signal(s) (peak: {max_finding:.0f})")

        # Calculate combined raw score
        if finding_score > 0:
            # If critical security violation detected, security engine dictates floor
            raw_score = max(finding_score, base_score + trust_mod + sensitive_mod)
        else:
            raw_score = base_score + trust_mod + sensitive_mod

        # Clamp between 0.0 and 100.0
        final_score = round(max(0.0, min(100.0, raw_score)), 1)

        # Classify Risk Level
        if final_score <= settings.RISK_THRESHOLD_LOW_MAX:
            classification = "Low"
        elif final_score <= settings.RISK_THRESHOLD_GUARDED_MAX:
            classification = "Guarded"
        elif final_score <= settings.RISK_THRESHOLD_MEDIUM_MAX:
            classification = "Medium"
        elif final_score <= settings.RISK_THRESHOLD_HIGH_MAX:
            classification = "High"
        else:
            classification = "Critical"

        # Determine Recommended Action
        if trust_level.lower() == "blocked" or final_score >= settings.AUTO_BLOCK_SCORE_THRESHOLD:
            recommended_action = "BLOCK"
        elif requires_manual_approval or final_score >= settings.APPROVAL_REQUIRED_SCORE_THRESHOLD:
            recommended_action = "REQUIRE_APPROVAL"
        else:
            recommended_action = "ALLOW"

        full_reasoning = " | ".join(reasons)

        return RiskAssessment(
            score=final_score,
            classification=classification,
            triggered_rules=triggered_rules,
            evidence={"reasons": reasons, "findings_count": len(security_findings)},
            reasoning=full_reasoning,
            recommended_action=recommended_action
        )

risk_engine = RiskScoringEngine()
