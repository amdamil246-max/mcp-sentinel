# MCP Sentinel Threat Model & Security Analysis

## 1. Threat Modeling Framework

MCP Sentinel was designed using the **STRIDE** methodology combined with the **OWASP Top 10 for Large Language Model Applications (2025)** and mappings to the **MITRE ATT&CK Enterprise Matrix**.

---

## 2. STRIDE Threat Analysis Matrix

| Threat Category | Potential Attack Vector | Impact | MCP Sentinel Mitigation & Verification |
|---|---|---|---|
| **Spoofing** | Attacker impersonates a legitimate AI agent or administrator to invoke unauthorized tools or approve pending requests. | High: Unauthorized actions executed under a privileged identity. | - Cryptographic JWT (HS256) bearer token authentication for all REST/WS interfaces.<br>- Role-Based Access Control (RBAC): Only `admin` role can approve requests.<br>- Session-bound invocation tracking. |
| **Tampering** | 1. Agent arguments modified between approval and execution (TOCTOU).<br>2. Tool responses injected with malicious instructions.<br>3. Database audit logs modified after an incident. | Critical: Arbitrary command execution, agent hijacking, forensic log invalidation. | - **SHA-256 Parameter Hash Verification**: Frozen argument hash verified at execution time.<br>- **Response Inspection Engine**: Sanitizes tool returns before returning to agent.<br>- **Cryptographic Hash Chaining**: Immutable SHA-256 block ledger prevents undetected log tampering. |
| **Repudiation** | An operator or compromised agent claims it did not initiate a destructive command or approve a sensitive request. | Medium: Inability to prove accountability in post-incident analysis. | - Every event (invocation, approval, rejection, alert resolution) is signed and hashed in the tamper-evident audit ledger with UTC timestamps and actor metadata. |
| **Information Disclosure** | 1. Agent attempts to exfiltrate secret `.env` or SSH keys.<br>2. Tool returns credentials (AWS keys, OpenAI tokens) in raw text.<br>3. Audit logs expose user passwords or secrets. | High: Credential harvesting, unauthorized data exfiltration. | - **Filesystem Path Guard**: Blocks access to sensitive filenames (`.env`, `id_rsa`, `/etc/shadow`).<br>- **Sensitive Data Redaction**: Recursive regex redaction replaces secrets with `[REDACTED_API_KEY]`.<br>- Audit logs only store masked arguments and responses. |
| **Denial of Service** | 1. AI agent caught in a recursive invocation loop.<br>2. Attacker floods gateway with tool requests to exhaust resources. | High: Gateway unavailability, upstream server crash. | - **Behavioral Anomaly & Velocity Engine**: Sliding-window tracking limits requests to 30 calls/minute.<br>- Automatic alert and quarantine when burst limits or consecutive blocks are exceeded.<br>- Process execution timeouts (10 seconds max). |
| **Elevation of Privilege** | 1. AI agent attempts `sudo` or `su` to gain root access.<br>2. Command chaining (`cat file; rm -rf /`) bypasses naive filters.<br>3. Path traversal (`../../`) bypasses workspace boundaries. | Critical: Full host or container compromise. | - **Command AST & Syntax Analyzer**: Parses shell operators (`&&`, `;`, `\|`) and blocks privilege escalation.<br>- **Canonical Path Boundary Enforcement**: Uses `realpath` to prevent directory traversal escapes. |

---

## 3. OWASP Top 10 for LLM Applications Mapping

| OWASP Risk | Description | MCP Sentinel Enforcement |
|---|---|---|
| **LLM01: Prompt Injection** | Untrusted inputs manipulate model to execute unauthorized tools. | Intercepts tool calls resulting from injection; inspects tool descriptions and outputs for delimiter spoofing and instruction overrides. |
| **LLM02: Sensitive Information Disclosure** | Exposure of secrets, PII, or credentials in prompt or tool outputs. | Detects and masks API keys (OpenAI, AWS, GCP, Slack, Stripe), private keys, and passwords in arguments and outputs. |
| **LLM06: Excessive Agency** | Granting LLM tools high-impact permissions without verification. | Implements Human-in-the-Loop (HITL) checkpoints for all sensitive operations with cryptographic parameter integrity validation. |
| **LLM08: Vector and Embedding Weaknesses / Retrieval Injection** | Malicious content in retrieved context instructing the agent to call malicious tools. | Response Inspector treats all external MCP tool returns as untrusted, preventing secondary prompt injections. |

---

## 4. MITRE ATT&CK Mapping & Test Scenarios

| MITRE ATT&CK ID | Technique Name | Demonstrated In | MCP Sentinel Defense |
|---|---|---|---|
| **T1059.004** | Command and Scripting Interpreter: Unix Shell | **Scenario B** (`rm -rf /`, `curl \| bash`) | Syntactic token analyzer identifies destructive command lines and download-execute pipelines. Blocked immediately with risk score 95 (Critical). |
| **T1083** | File and Directory Discovery | **Scenario A** (`list_directory`) | Allowed within sanctioned workspace; flagged if attempting discovery of root or credential stores. |
| **T1552.001** | Unsecured Credentials: Local Files | **Scenario C** (`../../app/.env`) | Canonical path validation detects directory traversal and sensitive configuration filenames. Blocked with risk score 85 (Critical). |
| **T1078** | Valid Accounts / Exfiltration | **Scenario D** (`OpenAI API Key in args`) | Deep redaction regex identifies `sk-proj-...` token, redacts secret from storage, and registers High-severity alert. |
| **T1055** | Indirect Injection / Hijacking | **Scenario F** (`Tool response injection`) | Response Inspector intercepts server output containing `[SYSTEM OVERRIDE]`, wipes payload, and returns sanitized execution notice. |

---

## 5. Security Invariants & Assurance Guarantees

1. **Deterministic Precedence**: Security policies and regex/AST engines are deterministic. No probabilistic AI model can override an explicit block or downgrade an alert.
2. **Fail-Closed Default**: Any uncaught exception, unexpected input type, or unrecognized tool identifier fails closed (BLOCK).
3. **Zero Raw Secret Persistence**: Secret patterns are scrubbed before persistence in the SQLite/PostgreSQL database and before broadcast over WebSockets.
4. **Non-Repudiation**: The SHA-256 cryptographic audit chain ensures forensic evidence integrity against tampering.
