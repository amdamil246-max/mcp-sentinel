import re
import copy
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel

class SecretFinding(BaseModel):
    rule_id: str
    rule_name: str
    threat_category: str = "SensitiveDataExposure"
    severity: str  # High, Critical, Medium
    risk_score: float
    description: str
    masked_preview: str

class SensitiveDataDetector:
    """
    Scans data for secrets, credentials, API keys, private keys, and passwords.
    Provides redaction utility for logs and responses.
    """

    SECRET_PATTERNS: List[Tuple[str, str, str, float, str]] = [
        # (Pattern, Rule Name, Severity, Risk Score, Redaction Tag)
        (r"-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----[\s\S]+?-----END (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----", "Cryptographic Private Key", "Critical", 95.0, "[REDACTED_PRIVATE_KEY]"),
        (r"\bAIza[0-9A-Za-z-_]{35}\b", "Google API Key", "High", 80.0, "[REDACTED_GOOGLE_API_KEY]"),
        (r"\bsk-(?:live-)?[a-zA-Z0-9]{32,48}\b", "OpenAI Secret Key", "High", 85.0, "[REDACTED_OPENAI_KEY]"),
        (r"\bAKIA[0-9A-Z]{16}\b", "AWS Access Key ID", "High", 75.0, "[REDACTED_AWS_KEY_ID]"),
        (r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,255}\b", "GitHub Personal Access Token", "High", 85.0, "[REDACTED_GITHUB_TOKEN]"),
        (r"\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*\b", "Slack API Token", "High", 80.0, "[REDACTED_SLACK_TOKEN]"),
        (r"\b(?:sk|pk)_(?:live|test)_[0-9a-zA-Z]{24,99}\b", "Stripe API Key", "High", 85.0, "[REDACTED_STRIPE_KEY]"),
        (r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b", "JSON Web Token (JWT)", "Medium", 65.0, "[REDACTED_JWT]"),
        (r"(?:postgres|mysql|mongodb(?:\+srv)?):\/\/[^:\s]+:[^@\s]+@[a-zA-Z0-9.-]+(?::[0-9]+)?\/[^\s\"']+", "Database Connection URI with Credentials", "Critical", 90.0, "[REDACTED_DB_URI]"),
    ]

    SENSITIVE_KEY_NAMES = {
        "password", "secret", "api_key", "apikey", "access_token", 
        "auth_token", "private_key", "client_secret", "bearer", "authorization"
    }

    def analyze(self, data: Any) -> List[SecretFinding]:
        findings: List[SecretFinding] = []
        text_repr = self._extract_strings(data)

        for text in text_repr:
            for pattern, name, severity, score, _ in self.SECRET_PATTERNS:
                matches = re.finditer(pattern, text)
                for match in matches:
                    val = match.group(0)
                    preview = val[:4] + "..." + val[-3:] if len(val) > 8 else "***"
                    findings.append(SecretFinding(
                        rule_id=f"SEC-{abs(hash(pattern)) % 10000:04d}",
                        rule_name=name,
                        severity=severity,
                        risk_score=score,
                        description=f"Detected sensitive credential: {name}",
                        masked_preview=preview
                    ))

        # Also inspect key-value dictionaries for explicit password/token keys
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(k, str) and k.lower() in self.SENSITIVE_KEY_NAMES:
                    if v and str(v).strip():
                        findings.append(SecretFinding(
                            rule_id="SEC-KEYWORD-MATCH",
                            rule_name=f"Sensitive Parameter Key ({k})",
                            severity="High",
                            risk_score=75.0,
                            description=f"Tool invocation argument contains sensitive keyword parameter: {k}",
                            masked_preview="[PROTECTED_VALUE]"
                        ))

        return findings

    def redact(self, data: Any) -> Any:
        """Deeply redacts all discovered secrets from strings, dictionaries, or lists."""
        if isinstance(data, str):
            redacted_str = data
            for pattern, _, _, _, tag in self.SECRET_PATTERNS:
                redacted_str = re.sub(pattern, tag, redacted_str)
            return redacted_str
        elif isinstance(data, dict):
            result = {}
            for k, v in data.items():
                if isinstance(k, str) and k.lower() in self.SENSITIVE_KEY_NAMES:
                    result[k] = "[REDACTED_SECRET]"
                else:
                    result[k] = self.redact(v)
            return result
        elif isinstance(data, list):
            return [self.redact(item) for item in data]
        return data

    def _extract_strings(self, data: Any) -> List[str]:
        strings = []
        if isinstance(data, str):
            strings.append(data)
        elif isinstance(data, dict):
            for v in data.values():
                strings.extend(self._extract_strings(v))
        elif isinstance(data, (list, tuple)):
            for item in data:
                strings.extend(self._extract_strings(item))
        return strings
