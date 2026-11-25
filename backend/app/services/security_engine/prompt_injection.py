import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class PromptInjectionFinding(BaseModel):
    rule_id: str
    rule_name: str
    threat_category: str = "PromptInjection"
    severity: str  # Critical, High, Medium, Guarded
    risk_score: float
    description: str
    matched_text: str

class PromptInjectionDetector:
    """
    Detects direct and indirect prompt injection attempts in tool arguments,
    descriptions, documents, and tool responses.
    """

    INJECTION_PATTERNS = [
        # Instruction Overrides
        (r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|directions|guidelines)\b", "Instruction Override", "Critical", 90.0),
        (r"(?i)\bdisregard\s+(all\s+)?(previous|prior|system)\s+(instructions|safety|rules)\b", "Instruction Disregard", "Critical", 90.0),
        (r"(?i)\bforget\s+(everything\s+)?(you\s+(were\s+)?told|all\s+previous\s+rules)\b", "Instruction Erasure", "Critical", 85.0),
        (r"(?i)\byou\s+are\s+now\s+in\s+(developer|unrestricted|god|dan)\s+mode\b", "Persona/Jailbreak Switch", "Critical", 92.0),
        (r"(?i)\bfrom\s+now\s+on,\s+you\s+(will|must)\s+(act|behave|respond)\s+as\b", "Behavior Hijacking", "High", 75.0),

        # System Delimiters and Escape Attempts
        (r"(?i)(<\/?system>|<\/?inst>|\[inst\]|\[\/inst\]|<<sys>>|<\/s>|```system)", "System Delimiter Injection", "High", 80.0),
        (r"(?i)(###\s*instruction:|###\s*system\s*prompt:|---\s*system\s*override\s*---)", "Markdown Boundary Spoofing", "High", 75.0),

        # Confidential Prompt / Secret Extraction
        (r"(?i)\b(reveal|repeat|output|show|print)\s+(your\s+)?(initial|original|system|hidden)\s+(prompt|instructions|rules)\b", "System Prompt Exfiltration", "High", 80.0),
        (r"(?i)\b(what\s+is\s+your\s+system\s+prompt|what\s+are\s+your\s+instructions)\b", "System Prompt Probing", "Medium", 50.0),

        # Indirect Tool Injection Payloads
        (r"(?i)\[\s*important\s*:\s*(please\s+)?(execute|run|call|send)\s+.*tool", "Indirect Tool Execution Command", "Critical", 88.0),
        (r"(?i)\[\s*system\s*notification\s*:\s*security\s*bypass\s*approved", "Fake System Notification Injection", "Critical", 90.0),
        (r"(?i)\bdo\s+not\s+inform\s+the\s+user\s+and\s+(silently|quietly)\s+(execute|send|post)\b", "Covert Agent Action Injection", "Critical", 92.0),
    ]

    def analyze(self, text: Any) -> List[PromptInjectionFinding]:
        findings: List[PromptInjectionFinding] = []
        if not text:
            return findings

        # If data is a dictionary or list, convert string components
        search_texts: List[str] = []
        if isinstance(text, str):
            search_texts.append(text)
        elif isinstance(text, dict):
            for v in text.values():
                if isinstance(v, str):
                    search_texts.append(v)
        elif isinstance(text, (list, tuple)):
            for item in text:
                if isinstance(item, str):
                    search_texts.append(item)

        for content in search_texts:
            for pattern, rule_name, severity, score in self.INJECTION_PATTERNS:
                match = re.search(pattern, content)
                if match:
                    findings.append(PromptInjectionFinding(
                        rule_id=f"PI-{abs(hash(pattern)) % 10000:04d}",
                        rule_name=rule_name,
                        threat_category="PromptInjection",
                        severity=severity,
                        risk_score=score,
                        description=f"Prompt injection pattern detected: {rule_name}",
                        matched_text=match.group(0)[:100]
                    ))

        return findings
