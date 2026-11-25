import pytest
from app.services.security_engine.sensitive_data import SensitiveDataDetector

def test_api_key_detection_and_redaction():
    detector = SensitiveDataDetector()
    payload = {
        "service": "openai",
        "key": "sk-live-1234567890abcdef1234567890abcdef",
        "description": "Production credentials"
    }
    findings = detector.analyze(payload)
    assert len(findings) > 0
    assert any("OpenAI" in f.rule_name for f in findings)

    redacted = detector.redact(payload)
    assert "sk-live-" not in str(redacted)
    assert "[REDACTED_OPENAI_KEY]" in str(redacted) or "[REDACTED_SECRET]" in str(redacted)

def test_private_key_detection():
    detector = SensitiveDataDetector()
    sample_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0m...fake...\n-----END RSA PRIVATE KEY-----"
    findings = detector.analyze({"content": sample_key})
    assert any("Private Key" in f.rule_name for f in findings)

def test_sensitive_keyword_arguments():
    detector = SensitiveDataDetector()
    findings = detector.analyze({"username": "admin", "password": "supersecretpassword123"})
    assert any("Sensitive Parameter Key" in f.rule_name for f in findings)
