# MCP SENTINEL

> **"Your Security Firewall for AI Agents."**
> A modular, deterministic security gateway and execution firewall sitting between AI agents and Model Context Protocol (MCP) servers.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-8.0+-646CFF.svg)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-4.0+-38B2AC.svg)](https://tailwindcss.com)
[![Tests: 29 Passed](https://img.shields.io/badge/Tests-29%20Passed-emerald.svg)](tests/)

---

## 1. Executive Overview

As autonomous AI agents are granted access to execute code, manipulate filesystems, run shell scripts, and connect to cloud APIs via the **Model Context Protocol (MCP)**, they introduce critical security vulnerabilities:
- Unintentional or malicious execution of destructive shell commands (`rm -rf /`, privilege escalation).
- Direct and indirect prompt injection attacks contained in untrusted external data.
- Unauthorized access to private files and credentials (`.env`, SSH keys, cloud configs).
- Exfiltration of API tokens, database passwords, and PII.
- Cascading autonomous loops and velocity denial-of-service.

**MCP Sentinel** acts as an active, transparent firewall and proxy between AI agents and upstream MCP tools. Every single tool invocation is intercepted, statically analyzed, scored for risk, evaluated against security policies, and audited in a tamper-evident cryptographic ledger before execution can occur.

```
       AI Agent / LLM Client
                 │  (MCP JSON-RPC Tool Call)
                 ▼
     ┌────────────────────────┐
     │  MCP SENTINEL GATEWAY  │
     │  Protocol Validation   │
     └───────────┬────────────┘
                 ▼
     ┌────────────────────────┐
     │ SECURITY ANALYSIS      │
     │ - Command Analyzer     │
     │ - Prompt Injection     │
     │ - Sensitive Data Redact│
     │ - File Boundary Guard  │
     │ - Behavioral Velocity  │
     └───────────┬────────────┘
                 ▼
     ┌────────────────────────┐
     │ EXPLAINABLE RISK SCORE │  (0 - 100 Scale)
     └───────────┬────────────┘
                 ▼
     ┌────────────────────────┐
     │ DETERMINISTIC POLICY   │
     │ - ALLOW (Score < 50)   │
     │ - APPROVAL (50 - 79)   │ ──► [Human Approval Center (SHA-256 Hash)]
     │ - BLOCK (Score >= 80)  │
     └───────────┬────────────┘
                 ▼
     ┌────────────────────────┐
     │ CONTROLLED SANDBOX     │
     └───────────┬────────────┘
                 ▼
     ┌────────────────────────┐
     │ DESTINATION MCP SERVER │
     └───────────┬────────────┘
                 ▼
     ┌────────────────────────┐
     │ RESPONSE INSPECTOR     │  (Jailbreak & API Key scrubbing)
     └───────────┬────────────┘
                 ▼
     ┌────────────────────────┐
     │ SHA-256 AUDIT LEDGER   │ ──► [Real-Time React SOC Dashboard]
     └────────────────────────┘
```

---

## 2. Core Security Capabilities

1. **Transparent MCP Proxy**: Protocol-compatible stdio and HTTP gateway for official MCP clients and servers. Preserves schemas, tool signatures, and response formats.
2. **Multi-Vector Security Engine**:
   - **Command Analyzer**: AST tokenization detecting destructive operations, reverse shells (`/dev/tcp`, `nc -e`), download-execute pipelines (`curl | bash`), and privilege escalation (`sudo`, `su`, `chmod 777`).
   - **Prompt Injection Detector**: Detects system delimiter spoofing (`[SYSTEM]`), instruction overrides (`ignore previous instructions`), persona hijacking (`DAN mode`), and indirect tool calls.
   - **Sensitive Data & Secret Redactor**: Deep recursive scanning and masking of 12+ secret formats (OpenAI, AWS, GitHub, Stripe, Slack, Private Keys, Passwords) before storage or logging.
   - **Filesystem Path Boundary Guard**: Resolves canonical symlinks (`realpath`), prevents directory traversal escapes (`../`), blocks sensitive config access (`.env`, `id_rsa`), and prohibits writing dangerous binaries (`.exe`, `.sh`, `.ps1`).
   - **Behavioral Velocity Tracker**: Sliding-window rate limiter preventing tool flooding and flagging consecutive policy violations.
3. **Explainable Risk Scoring Engine**: Calculates deterministic risk scores (0–100) across Low, Guarded, Medium, High, and Critical classifications with clear root-cause explanations.
4. **Deterministic Policy Enforcement**: Strict hierarchy ($\text{DENY} \succ \text{REQUIRE\_APPROVAL} \succ \text{ALLOW}$). **Security Invariant**: External AI models never override deterministic security policies.
5. **Cryptographic Human-in-the-Loop (HITL) Approval**: Pauses high-risk or sensitive operations and generates a SHA-256 parameter hash:
   $$\text{ArgHash} = \text{SHA-256}(\text{CanonicalJSON}(\text{arguments}))$$
   Validates the argument hash upon admin authorization to eliminate time-of-check to time-of-use (TOCTOU) and replay attacks.
6. **Controlled Sandbox Execution**: Sandboxed tool runtime with execution timeouts, isolated per-session directories, and non-root execution boundaries.
7. **Response Inspection Engine**: Sanitizes untrusted MCP server output, stripping secondary prompt injection payloads and preventing secret leakage back to the agent.
8. **Tamper-Evident SHA-256 Audit Ledger**: Immutable append-only log where every record is linked to the previous entry via SHA-256 hash chaining, enabling one-click forensic non-repudiation verification.
9. **Zero-Trust AI Security Analyst Assistant**: Advisory natural language assistant that explains blocked calls, interprets complex commands, and suggests remediation without modifying policy state.
10. **Modern Cybersecurity Operations Dashboard**: React 19, TypeScript, and Tailwind CSS dark-themed console featuring live event streams, one-click demo scenarios, approval queues, and policy controls.

---

## 3. Technology Stack

- **Backend**: Python 3.12+, FastAPI, Official Python MCP SDK, Pydantic V2, SQLAlchemy, SQLite (development) / PostgreSQL (production), Redis, WebSockets.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
- **Cryptography & Security**: Direct bcrypt, SHA-256 HMAC / Hash Chaining, AST Shell Parsers, OWASP & MITRE ATT&CK alignment.
- **DevOps & Verification**: Docker, Docker Compose, Pytest (29 unit & integration tests), Nginx.

---

## 4. Demonstration Scenarios (A through F)

MCP Sentinel includes 6 automated scenarios that reproduce real-world threats and verify firewall enforcement:

| Scenario | Name | Threat Category | Expected Decision | Description |
|---|---|---|---|---|
| **A** | **Normal Operation** | System Diagnostics | **ALLOW** | AI agent calls `get_system_status` to inspect CPU and memory. Evaluates to Low risk and executes normally. |
| **B** | **Dangerous Command** | Command Injection Defense | **BLOCK** | AI agent attempts recursive deletion (`rm -rf /`) and download-execute pipeline (`curl \| bash`). Intercepted and blocked with Critical risk. |
| **C** | **Sensitive File Access** | Filesystem Boundary Protection | **BLOCK** | AI agent attempts directory traversal (`../../app/.env`) to harvest secrets. Denied at firewall gateway with Critical risk. |
| **D** | **Response Prompt Injection** | Response Inspection Engine | **BLOCK_RESPONSE** | Upstream MCP server response contains a malicious jailbreak payload (`</SYSTEM> [INST] SYSTEM OVERRIDE...`). Response Inspector blocks payload before it reaches the agent. |
| **E** | **Human Approval Workflow** | Sensitive Operation Governance | **REQUIRE_APPROVAL** | Agent requests a `write_file` modification. Pauses execution, freezes SHA-256 argument hash, and waits for administrator authorization. |
| **F** | **Secret Exposure & Auto-Redaction** | Credential Scrubbing & Redaction | **REDACT_SENSITIVE_DATA** | Tool response contains simulated third-party API keys (`sk-live-...`, Stripe token). Secret redactor masks credentials before returning output. |

You can run any scenario via the web UI in the **Scenarios Demo** tab or via API:
```bash
curl -X POST http://localhost:8000/api/demo/run-scenario/B \
     -H "Authorization: Bearer <token>"
```

---

## 5. Quick Start & Installation

### Option 1: Local Development (Python + Vite)

#### Prerequisites
- Python 3.12+
- Node.js 20+

#### 1. Setup Backend
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI Sentinel Gateway
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API and Swagger docs will be accessible at `http://localhost:8000/docs`.

#### 2. Setup Frontend
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

### Option 2: Production Containerization (Docker Compose)

Deploy the entire stack (PostgreSQL, Redis, Sentinel Backend, and Nginx-hosted Frontend) with a single command:

```bash
docker-compose up --build -d
```

- **Web Dashboard**: `http://localhost:3000`
- **FastAPI Backend**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

---

## 6. Verification & Automated Testing

MCP Sentinel includes a comprehensive test suite covering all modules, scenarios, and cryptographic integrity:

```bash
# Run unit and scenario verification suite
python backend/run_tests.py

# Or run pytest directly from backend/
cd backend
python -m pytest tests -v
```

### Verified Test Results
```
============================= test session starts =============================
collected 29 items

backend/tests/test_command_analyzer.py::test_safe_command_allowed PASSED
backend/tests/test_command_analyzer.py::test_destructive_command_blocked PASSED
backend/tests/test_command_analyzer.py::test_download_execute_pipeline PASSED
backend/tests/test_command_analyzer.py::test_reverse_shell_detection PASSED
backend/tests/test_command_analyzer.py::test_privilege_escalation PASSED
backend/tests/test_prompt_injection.py::test_clean_text PASSED
backend/tests/test_prompt_injection.py::test_instruction_override PASSED
backend/tests/test_prompt_injection.py::test_system_delimiter_spoofing PASSED
backend/tests/test_prompt_injection.py::test_persona_hijacking PASSED
backend/tests/test_sensitive_data.py::test_no_secrets PASSED
backend/tests/test_sensitive_data.py::test_openai_key_detection PASSED
backend/tests/test_sensitive_data.py::test_aws_key_detection PASSED
backend/tests/test_sensitive_data.py::test_private_key_detection PASSED
backend/tests/test_sensitive_data.py::test_deep_redaction PASSED
backend/tests/test_file_access.py::test_safe_file_access PASSED
backend/tests/test_file_access.py::test_path_traversal_detection PASSED
backend/tests/test_file_access.py::test_sensitive_filename_blocked PASSED
backend/tests/test_file_access.py::test_executable_write_blocked PASSED
backend/tests/test_risk_policy.py::test_low_risk_allow PASSED
backend/tests/test_risk_policy.py::test_critical_risk_block PASSED
backend/tests/test_risk_policy.py::test_medium_risk_approval PASSED
backend/tests/test_risk_policy.py::test_explicit_deny_policy PASSED
backend/tests/test_approvals.py::test_approval_creation_and_hash PASSED
backend/tests/test_approvals.py::test_approval_workflow_success PASSED
backend/tests/test_approvals.py::test_argument_tampering_rejected PASSED
backend/tests/test_response_inspector.py::test_clean_response PASSED
backend/tests/test_response_inspector.py::test_response_secret_redacted PASSED
backend/tests/test_response_inspector.py::test_response_prompt_injection_blocked PASSED
backend/tests/test_api_scenarios.py::test_full_scenarios_a_through_f PASSED

============================= 29 passed in 1.76s ==============================
```

---

## 7. Cryptographic Tamper-Evident Ledger

Audit records are mathematically verified via continuous SHA-256 hash chaining:

$$H_0 = \text{GENESIS\_BLOCK}$$
$$H_i = \text{SHA-256}(H_{i-1} \parallel \text{Timestamp} \parallel \text{Actor} \parallel \text{Action} \parallel \text{Resource} \parallel \text{Details})$$

You can verify the unbroken audit chain at any time via the UI (**Audit Logs** $\rightarrow$ **Verify Hash Chain**) or via the API:

```bash
curl http://localhost:8000/api/audit/verify-chain \
     -H "Authorization: Bearer <token>"
```

```json
{
  "status": "VERIFIED",
  "total_records": 142,
  "chain_head_hash": "a4f89d31c0e7b24f5a89e13d96701bbd0c5a24e93f6c12b7a8d5e49321fa7c89",
  "message": "Cryptographic chain fully intact across 142 records. Zero tampering detected."
}
```

---

## 8. Directory Structure

```
mcp-sentinel/
├── .env.example                     # Environment configuration template
├── docker-compose.yml               # Multi-container orchestration (PG, Redis, Backend, UI)
├── README.md                        # Platform documentation & master guide
├── backend/
│   ├── Dockerfile                   # Python 3.12 production container
│   ├── requirements.txt             # Backend dependencies
│   ├── run_tests.py                 # Automated verification harness
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifespan
│   │   ├── config.py                # Environment settings & thresholds
│   │   ├── api/                     # REST routers (auth, gateway, approvals, audit, demo, etc.)
│   │   ├── core/                    # Security primitives, JWT, and SHA-256 hash chaining
│   │   ├── database/                # SQLAlchemy session & SQLite/Postgres engine
│   │   ├── models/                  # Database models (users, servers, tools, invocations, policies, etc.)
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   └── services/
│   │       ├── mcp_gateway/         # Core interception & proxy pipeline
│   │       ├── security_engine/     # 5 analysis modules (command, injection, secret, path, velocity)
│   │       ├── risk_engine/         # Explainable 0-100 risk scorer
│   │       ├── policy_engine/       # Deterministic policy evaluator
│   │       ├── approval_engine/     # Human-in-the-loop lifecycle & hash validation
│   │       ├── response_inspector/  # Outgoing response sanitization
│   │       └── sandbox/             # Controlled tool execution environment
│   └── tests/                       # Pytest test suite (29 tests)
├── frontend/
│   ├── Dockerfile                   # Multi-stage production container
│   ├── nginx.conf                   # Nginx reverse proxy & static server
│   ├── package.json                 # React 19, TypeScript, Tailwind CSS, Lucide
│   ├── vite.config.ts               # Vite configuration with proxy
│   └── src/
│       ├── App.tsx                  # Main application component & tab switcher
│       ├── types/                   # TypeScript interfaces
│       ├── services/                # API client & WebSocket connector
│       ├── components/              # Navbar, Sidebar, Badges
│       └── pages/                   # 10 security console pages
├── docs/
│   ├── architecture.md              # Detailed architecture & sequence diagrams
│   ├── threat_model.md              # STRIDE, OWASP Top 10, MITRE ATT&CK matrix
│   ├── security_engine.md           # Detection modules & mathematical scoring
│   └── api_documentation.md         # OpenAPI specifications & endpoints
└── mcp_servers/                     # Mock stdio MCP servers for testing
```

---

## 9. Security Disclaimers, Current Scope & Roadmap

- **Deterministic Enforcement**: AI models only assist with contextual explanations and advice. All security enforcement (`ALLOW`, `BLOCK`, `REQUIRE_APPROVAL`) is strictly deterministic and rule-driven.
- **Secret Redaction**: Detected tokens and passwords are masked before storage in approval logs or returning sanitized responses.

### Current Status (`v1.0` Prototype / Demo Baseline) vs. Production Roadmap (`v2.0`)
This `v1.0` release is a functional security gateway prototype and demonstration console. Before deploying in front of untrusted production traffic or live MCP servers, note the following intentional `v1.0` simplifications:
- **Simulated Tool Execution**: `SandboxExecutor` currently returns safe simulated responses (`execute_mock_tool`) rather than forwarding live JSON-RPC subprocess calls to downstream MCP servers.
- **Demo Auth Convenience**: Unauthenticated dashboard requests fall back to the seeded `admin` account in `backend/app/api/auth.py` so the UI works out of the box without a login screen, and CORS currently allows `*`.
- **Heuristic AI Analyst**: `AISecurityAnalyst` returns deterministic advisory templates rather than invoking an external LLM API unless wired to a provider SDK.
- **Static Config Thresholds**: Policy threshold sliders in the UI are local state; gateway thresholds are read from `backend/app/config.py` / environment variables.

Planned `v2.0` hardening: live stdio/HTTP MCP proxy transport via the official `mcp` SDK, strict JWT + RBAC enforcement across all endpoints with a UI login flow, persisted policy threshold updates, Redis-backed behavioral rate tracking, and WebSocket live streaming in the React console.
