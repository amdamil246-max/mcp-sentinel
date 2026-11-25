import json
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel
from app.services.security_engine.sensitive_data import SensitiveDataDetector
from app.services.security_engine.prompt_injection import PromptInjectionDetector

class ResponseInspectionResult(BaseModel):
    action: str  # ALLOW_RESPONSE, REDACT_SENSITIVE_DATA, BLOCK_RESPONSE, FLAG_FOR_REVIEW
    sanitized_response: Any
    findings: List[Dict[str, Any]]
    secrets_redacted_count: int = 0
    injection_detected: bool = False
    explanation: str

class ResponseInspector:
    """
    Inspects responses returned by MCP tools before they reach the AI Agent.
    Prevents downstream prompt injection attacks and secret leaks.
    """

    def __init__(self):
        self.secret_detector = SensitiveDataDetector()
        self.pi_detector = PromptInjectionDetector()

    def inspect(self, raw_response: Any) -> ResponseInspectionResult:
        findings: List[Dict[str, Any]] = []
        action = "ALLOW_RESPONSE"
        explanation = "Response inspected and verified safe."
        
        # 1. Detect Prompt Injection in Response Data
        pi_findings = self.pi_detector.analyze(raw_response)
        for pf in pi_findings:
            findings.append(pf.model_dump())

        # If critical prompt injection detected in output, BLOCK the response to shield agent
        if any(f.severity == "Critical" for f in pi_findings):
            return ResponseInspectionResult(
                action="BLOCK_RESPONSE",
                sanitized_response={
                    "error": "MCP Sentinel Security Gate blocked tool response: malicious prompt injection instructions detected in external tool payload."
                },
                findings=findings,
                secrets_redacted_count=0,
                injection_detected=True,
                explanation="Blocked tool response containing dangerous prompt injection payload."
            )
        elif pi_findings:
            action = "FLAG_FOR_REVIEW"
            explanation = "Response contains suspicious instructional patterns; flagged for review."

        # 2. Detect & Redact Secrets in Response Data
        secret_findings = self.secret_detector.analyze(raw_response)
        for sf in secret_findings:
            findings.append(sf.model_dump())

        if secret_findings:
            sanitized = self.secret_detector.redact(raw_response)
            if action != "FLAG_FOR_REVIEW":
                action = "REDACT_SENSITIVE_DATA"
            explanation = f"Sanitized response by redacting {len(secret_findings)} secret(s)/credential(s)."
            return ResponseInspectionResult(
                action=action,
                sanitized_response=sanitized,
                findings=findings,
                secrets_redacted_count=len(secret_findings),
                injection_detected=bool(pi_findings),
                explanation=explanation
            )

        return ResponseInspectionResult(
            action=action,
            sanitized_response=raw_response,
            findings=findings,
            secrets_redacted_count=0,
            injection_detected=bool(pi_findings),
            explanation=explanation
        )

response_inspector = ResponseInspector()
