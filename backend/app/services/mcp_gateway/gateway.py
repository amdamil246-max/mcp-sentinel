import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.server import MCPServer
from app.models.tool import RegisteredTool
from app.models.invocation import ToolInvocation
from app.models.security import SecurityAnalysis, SecurityAlert
from app.models.approval import ApprovalRequest
from app.models.audit import AuditLog

from app.services.security_engine import security_engine
from app.services.risk_engine.scorer import risk_engine
from app.services.policy_engine.evaluator import policy_engine
from app.services.approval_engine.manager import approval_engine
from app.services.sandbox.executor import sandbox_executor
from app.services.response_inspector.inspector import response_inspector

from app.core.security import compute_audit_hash

class MCPGateway:
    """
    Core MCP Gateway Engine.
    Intercepts, analyzes, controls, and audits every MCP tool invocation.
    Ensures complete security firewall enforcement for AI agents.
    """

    def intercept_and_execute(
        self,
        db: Session,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: str = "default-session",
        user_id: str = "agent-system"
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        invocation_id = f"inv-{uuid.uuid4().hex[:12]}"

        # 1. Fetch Server & Tool Metadata
        server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
        tool = db.query(RegisteredTool).filter(
            RegisteredTool.server_id == server_id,
            RegisteredTool.name == tool_name
        ).first()

        is_server_enabled = server.is_enabled if server else False
        is_tool_enabled = tool.is_enabled if tool else (True if server else False)
        perm_level = tool.permission_level if tool else "execute"
        trust_level = tool.trust_level if tool else "untrusted"
        requires_approval_flag = tool.requires_approval if tool else False

        # 2. Record initial Tool Invocation
        invocation = ToolInvocation(
            id=invocation_id,
            session_id=session_id,
            user_id=user_id,
            server_id=server_id,
            tool_name=tool_name,
            arguments=arguments,
            status="analyzing",
            risk_score=0.0,
            risk_classification="Low",
            decision="ALLOW",
            approval_status="NOT_REQUIRED",
            execution_status="NOT_EXECUTED",
            created_at=datetime.utcnow()
        )
        db.add(invocation)
        db.commit()

        # 3. Execute Security Analysis Engine Modules
        sec_result = security_engine.inspect_request(
            server_id=server_id,
            tool_name=tool_name,
            arguments=arguments,
            session_id=session_id
        )

        # 4. Calculate Explainable Risk Score
        risk_assessment = risk_engine.calculate_risk(
            security_findings=sec_result.findings,
            permission_level=perm_level,
            trust_level=trust_level,
            is_sensitive_tool=requires_approval_flag,
            requires_manual_approval=requires_approval_flag
        )

        # 5. Evaluate Against Policy Engine
        policy_decision = policy_engine.evaluate(
            risk_assessment=risk_assessment,
            is_tool_enabled=is_tool_enabled,
            is_server_enabled=is_server_enabled,
            explicit_approval_required=requires_approval_flag
        )

        # Inform behavioral tracker
        security_engine.behavior_detector.record_decision(session_id, policy_decision.decision)

        # 6. Persist Security Analysis Record
        sec_analysis = SecurityAnalysis(
            id=f"sa-{uuid.uuid4().hex[:12]}",
            invocation_id=invocation_id,
            risk_score=risk_assessment.score,
            risk_classification=risk_assessment.classification,
            triggered_rules=risk_assessment.triggered_rules,
            evidence=sec_result.evidence,
            reasoning=risk_assessment.reasoning,
            created_at=datetime.utcnow()
        )
        db.add(sec_analysis)

        # 7. Create Security Alerts if High/Critical Threats Detected
        if sec_result.findings and (risk_assessment.score >= 60.0 or sec_result.has_critical_findings):
            for finding in sec_result.findings:
                if finding.get("severity") in ("High", "Critical"):
                    alert = SecurityAlert(
                        id=f"alt-{uuid.uuid4().hex[:12]}",
                        invocation_id=invocation_id,
                        threat_category=finding.get("threat_category", "GeneralThreat"),
                        severity=finding.get("severity", "High"),
                        title=finding.get("rule_name", "Security Alert"),
                        description=finding.get("description", "A security policy violation was detected."),
                        evidence={"snippet": finding.get("command_snippet") or finding.get("matched_text") or finding.get("target_path")},
                        affected_tool=f"{server_id}:{tool_name}",
                        status="NEW",
                        created_at=datetime.utcnow()
                    )
                    db.add(alert)

        # 8. Record Immutable Audit Log with Cryptographic Hash Chaining
        last_log = db.query(AuditLog).order_by(AuditLog.created_at.desc()).first()
        prev_hash = last_log.entry_hash if last_log else "GENESIS"
        
        now_ts = datetime.utcnow()
        audit_details = {
            "invocation_id": invocation_id,
            "server_id": server_id,
            "tool_name": tool_name,
            "decision": policy_decision.decision,
            "risk_score": risk_assessment.score,
            "reasons": policy_decision.reasons_list
        }
        entry_hash = compute_audit_hash(
            prev_hash, "TOOL_INVOCATION", user_id, policy_decision.decision, audit_details, now_ts
        )
        audit_entry = AuditLog(
            id=f"aud-{uuid.uuid4().hex[:12]}",
            event_type="TOOL_INVOCATION",
            actor=user_id,
            target_resource=f"{server_id}/{tool_name}",
            action=policy_decision.decision,
            details=audit_details,
            previous_hash=prev_hash,
            entry_hash=entry_hash,
            created_at=now_ts
        )
        db.add(audit_entry)

        # 9. Enforce Decision
        invocation.risk_score = risk_assessment.score
        invocation.risk_classification = risk_assessment.classification
        invocation.decision = policy_decision.decision

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        invocation.execution_duration_ms = duration_ms

        # DECISION: BLOCK
        if policy_decision.decision == "BLOCK":
            invocation.status = "blocked"
            invocation.execution_status = "BLOCKED"
            invocation.response_data = {"blocked_reason": policy_decision.reason, "reasons": policy_decision.reasons_list}
            db.commit()

            return {
                "invocation_id": invocation_id,
                "decision": "BLOCK",
                "risk_score": risk_assessment.score,
                "risk_classification": risk_assessment.classification,
                "status": "blocked",
                "reasons": policy_decision.reasons_list,
                "result": {"error": f"Tool invocation blocked by MCP Sentinel: {policy_decision.reason}"},
                "execution_duration_ms": duration_ms
            }

        # DECISION: REQUIRE_APPROVAL
        elif policy_decision.decision == "REQUIRE_APPROVAL":
            invocation.status = "pending_approval"
            invocation.approval_status = "PENDING"
            db.commit()

            approval_req = approval_engine.create_request(
                db=db,
                invocation_id=invocation_id,
                tool_name=f"{server_id}:{tool_name}",
                server_name=server.name if server else server_id,
                arguments=arguments,
                risk_score=risk_assessment.score,
                reasons=policy_decision.reasons_list,
                requested_by=user_id
            )

            return {
                "invocation_id": invocation_id,
                "decision": "REQUIRE_APPROVAL",
                "risk_score": risk_assessment.score,
                "risk_classification": risk_assessment.classification,
                "status": "pending_approval",
                "approval_id": approval_req.id,
                "reasons": policy_decision.reasons_list,
                "result": {
                    "status": "HOLD",
                    "message": "Operation suspended pending security administrator approval.",
                    "approval_id": approval_req.id
                },
                "execution_duration_ms": duration_ms
            }

        # DECISION: ALLOW -> Controlled Execution & Response Inspection
        else:
            invocation.status = "executing"
            exec_res = sandbox_executor.execute_mock_tool(server_id, tool_name, arguments)
            inspected = response_inspector.inspect(exec_res.data)

            invocation.status = "completed"
            invocation.execution_status = "SUCCESS" if exec_res.success else "ERROR"
            invocation.response_data = inspected.sanitized_response
            
            total_duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            invocation.execution_duration_ms = total_duration_ms
            db.commit()

            return {
                "invocation_id": invocation_id,
                "decision": "ALLOW",
                "risk_score": risk_assessment.score,
                "risk_classification": risk_assessment.classification,
                "status": "completed",
                "reasons": policy_decision.reasons_list,
                "result": inspected.sanitized_response,
                "response_inspection": {
                    "action": inspected.action,
                    "explanation": inspected.explanation,
                    "secrets_redacted": inspected.secrets_redacted_count
                },
                "execution_duration_ms": total_duration_ms
            }

    def execute_approved_invocation(
        self,
        db: Session,
        approval_id: str,
        execution_arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
        if not approval:
            raise ValueError(f"Approval request '{approval_id}' not found.")

        if approval.status != "APPROVED":
            raise ValueError(f"Approval status is '{approval.status}', expected 'APPROVED'.")

        if not approval_engine.verify_arguments_integrity(approval, execution_arguments):
            raise ValueError("Argument integrity check failed: tool arguments have been modified since approval was granted.")

        invocation = db.query(ToolInvocation).filter(ToolInvocation.id == approval.invocation_id).first()
        if not invocation:
            raise ValueError("Invocation record not found.")

        parts = approval.tool_name.split(":", 1)
        server_id = parts[0] if len(parts) > 1 else invocation.server_id
        tool_name = parts[1] if len(parts) > 1 else invocation.tool_name

        exec_res = sandbox_executor.execute_mock_tool(server_id, tool_name, execution_arguments)
        inspected = response_inspector.inspect(exec_res.data)

        invocation.status = "completed"
        invocation.execution_status = "SUCCESS"
        invocation.response_data = inspected.sanitized_response
        invocation.execution_duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        db.commit()

        return {
            "invocation_id": invocation.id,
            "decision": "APPROVED_AND_EXECUTED",
            "status": "completed",
            "result": inspected.sanitized_response
        }

gateway = MCPGateway()
