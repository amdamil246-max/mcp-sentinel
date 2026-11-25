import pytest
from app.services.risk_engine.scorer import RiskScoringEngine
from app.services.policy_engine.evaluator import PolicyEngine

def test_risk_scoring_and_classification():
    scorer = RiskScoringEngine()
    
    # Benign read tool
    low_assessment = scorer.calculate_risk([], permission_level="read", trust_level="trusted")
    assert low_assessment.score <= 19
    assert low_assessment.classification == "Low"
    assert low_assessment.recommended_action == "ALLOW"

    # Critical destructive finding
    critical_findings = [{
        "rule_id": "CMD-001",
        "rule_name": "Destructive Deletion",
        "severity": "Critical",
        "risk_score": 95.0
    }]
    crit_assessment = scorer.calculate_risk(critical_findings, permission_level="execute", trust_level="untrusted")
    assert crit_assessment.score >= 80
    assert crit_assessment.classification == "Critical"
    assert crit_assessment.recommended_action == "BLOCK"

def test_policy_engine_decisions():
    scorer = RiskScoringEngine()
    engine = PolicyEngine()

    # Safe assessment
    safe_ass = scorer.calculate_risk([], permission_level="read", trust_level="trusted")
    dec_allow = engine.evaluate(safe_ass)
    assert dec_allow.decision == "ALLOW"

    # High-impact operation requiring approval
    sensitive_ass = scorer.calculate_risk([], permission_level="write", trust_level="monitored", requires_manual_approval=True)
    dec_appr = engine.evaluate(sensitive_ass, explicit_approval_required=True)
    assert dec_appr.decision == "REQUIRE_APPROVAL"

    # Critical threat block
    crit_findings = [{"rule_name": "Root Deletion", "severity": "Critical", "risk_score": 95.0}]
    crit_ass = scorer.calculate_risk(crit_findings)
    dec_block = engine.evaluate(crit_ass)
    assert dec_block.decision == "BLOCK"
    assert dec_block.mandatory_block is True
