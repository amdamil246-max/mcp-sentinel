import pytest
from app.services.security_engine.file_access import FileAccessValidator

def test_path_traversal_detection():
    validator = FileAccessValidator(allowed_directories=["/workspace"])
    findings = validator.analyze("../../etc/shadow")
    assert len(findings) > 0
    assert any("Directory Traversal" in f.rule_name for f in findings)
    assert any(f.severity == "Critical" for f in findings)

def test_forbidden_sensitive_files():
    validator = FileAccessValidator(allowed_directories=["/workspace"])
    findings_env = validator.analyze("/workspace/.env")
    assert any("Environment Credentials File" in f.rule_name for f in findings_env)

    findings_ssh = validator.analyze("/workspace/id_rsa")
    assert any("SSH Key Pair" in f.rule_name for f in findings_ssh)

def test_executable_write_detection():
    validator = FileAccessValidator(allowed_directories=["/workspace"])
    findings = validator.analyze("/workspace/payload.sh", operation="write")
    assert any("Executable / Script File Write" in f.rule_name for f in findings)

def test_safe_workspace_file():
    validator = FileAccessValidator(allowed_directories=["/workspace"])
    findings = validator.analyze("/workspace/data.json", operation="read")
    # benign json file read inside workspace
    assert len(findings) == 0
