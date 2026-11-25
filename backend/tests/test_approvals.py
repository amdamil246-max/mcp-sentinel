import pytest
from app.services.approval_engine.manager import ApprovalEngine
from app.models.approval import ApprovalRequest
from app.core.security import compute_arguments_hash

def test_argument_hash_integrity_and_anti_tampering():
    engine = ApprovalEngine()
    original_args = {"path": "/workspace/config.json", "content": "valid"}
    args_hash = compute_arguments_hash(original_args)

    req = ApprovalRequest(
        id="test-appr-1",
        invocation_id="inv-1",
        tool_name="filesystem-server:write_file",
        server_name="filesystem-server",
        arguments_hash=args_hash,
        redacted_arguments=original_args,
        risk_score=50.0,
        reasons=["High impact write"],
        status="APPROVED"
    )

    # Identical arguments should verify true
    assert engine.verify_arguments_integrity(req, {"path": "/workspace/config.json", "content": "valid"}) is True

    # Modified arguments should fail verification immediately!
    assert engine.verify_arguments_integrity(req, {"path": "/etc/shadow", "content": "tampered"}) is False
