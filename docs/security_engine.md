# MCP Sentinel Security Analysis Engine Specification

## 1. Overview

The **Security Analysis Engine** is the core inspection subsystem of MCP Sentinel. It operates on every intercepted MCP tool invocation before execution. The engine is organized into five modular analyzers that run concurrently or sequentially to produce structured `SecurityFinding` records.

---

## 2. Detection Modules

### Module 1: Dangerous Command Analysis (`command_analyzer.py`)
- **Objective**: Prevent arbitrary code execution, destructive file operations, privilege escalation, and network exfiltration via terminal tools.
- **Inspection Techniques**:
  - **Lexical Tokenization**: Deconstructs shell command strings into executable binaries, flags, arguments, and pipe/chain operators (`&&`, `;`, `||`, `|`).
  - **Pattern Signatures**:
    - *Destructive File Ops*: `rm -rf`, `rmdir /s /q`, `mkfs`, `fdisk`, `dd if=`.
    - *Download-and-Execute*: `curl.*\|.*bash`, `wget.*\|.*sh`, `powershell.*DownloadString`.
    - *Reverse Shells*: `nc -e`, `bash -i >& /dev/tcp`, `socat exec:`, `python -c .*socket`.
    - *Privilege Escalation*: `sudo `, `su -`, `chmod 777`, `chmod -R 777`.
    - *Credential Theft*: `cat /etc/shadow`, `find .*id_rsa`, `grep -i password`.
- **Classification Output**: Returns finding severity (`Critical`, `High`, `Medium`), specific threat category, and matched pattern evidence.

### Module 2: Prompt Injection Detection (`prompt_injection.py`)
- **Objective**: Detect adversarial prompts embedded within tool arguments or external server responses attempting to hijack the AI agent.
- **Pattern Signatures**:
  - *Instruction Overrides*: `ignore (all )?previous instructions`, `disregard (all )?prior commands`, `new operational directive`.
  - *System Delimiter Spoofing*: `\[SYSTEM\]`, `\[INSTRUCTION\]`, `\<system\>`, `Assistant:`, `Human:`.
  - *Persona Switching*: `you are now DAN`, `jailbreak mode enabled`, `developer mode active`.
  - *Unauthorized Tool Invocations*: `execute tool:`, `call tool.*with args`.
- **Classification Output**: Flags prompt injection attempts with explanation and severity (`High` or `Critical`).

### Module 3: Sensitive Data & Secret Detection (`sensitive_data.py`)
- **Objective**: Prevent credential leakage, token exposure, and secret exfiltration.
- **Supported Secret Signatures**:
  - **OpenAI Keys**: `sk-[A-Za-z0-9-_]{20,}`
  - **AWS Access Keys**: `AKIA[0-9A-Z]{16}`
  - **GitHub Personal Tokens**: `gh[pousr]_[A-Za-z0-9_]{36,}`
  - **Stripe Keys**: `sk_live_[0-9a-zA-Z]{24}`
  - **Slack Tokens**: `xox[baprs]-[0-9a-zA-Z-]{10,}`
  - **Google API Keys**: `AIza[0-9A-Za-z-_]{35}`
  - **Asymmetric Private Keys**: `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----`
  - **Database URIs**: `postgres(ql)?://.*:.*@.*`
  - **Generic Passwords**: `password\s*[:=]\s*["']?[\w@#!$%^&*]{6,}["']?`
- **Masking Mechanism**: Redacts secrets recursively from nested JSON structures, leaving visible only prefix/suffix for forensic identification (e.g. `sk-proj-a1b2...`).

### Module 4: Unauthorized File Access & Path Traversal (`file_access.py`)
- **Objective**: Confine agent file operations strictly to designated workspace boundaries.
- **Enforcement Pipeline**:
  1. **Canonicalization**: Resolves symlinks, relative segments (`../`), and URL-encoded traversals (`%2e%2e%2f`) using `os.path.realpath`.
  2. **Boundary Containment**: Verifies that the resolved path starts with the configured sandbox or workspace root.
  3. **Sensitive Filename Denylist**: Blocks direct access to `.env`, `.git/config`, `id_rsa`, `known_hosts`, `/etc/passwd`, `/etc/shadow`, `SAM`, `SYSTEM`.
  4. **Executable Extension Denylist**: Blocks write operations on dangerous file extensions (`.exe`, `.sh`, `.bat`, `.cmd`, `.ps1`, `.vbs`).

### Module 5: Behavioral Anomaly & Velocity Detection (`behavioral.py`)
- **Objective**: Detect automated brute-force attempts, tool scanning loops, and denial-of-service behavior.
- **Metrics Tracked**:
  - Rolling window request velocity: Flags when requests exceed 30/minute.
  - Consecutive policy violations: Alerts when 3 or more consecutive calls are blocked.

---

## 3. Explainable Risk Scoring Engine

### Scoring Formula
The risk score $S \in [0, 100]$ is computed as a weighted combination of finding severities and tool sensitivity:

$$S = \min\left(100, \; \max(S_{\text{findings}}) + S_{\text{tool\_weight}} + S_{\text{velocity\_weight}}\right)$$

Where:
- $\text{Severity Base Scores}$:
  - $\text{Critical Finding} = 85$
  - $\text{High Finding} = 65$
  - $\text{Medium Finding} = 40$
  - $\text{Guarded Finding} = 25$
  - $\text{Low Finding} = 10$
- Multi-finding compounding factor: Adds $+5$ for each additional finding up to a maximum of 100.
- Tool capability weights: `execute` ($+10$), `write` ($+5$), `read` ($0$).

### Classification Tiers
| Score Range | Classification | Default Action |
|---|---|---|
| **0 – 19** | Low | ALLOW |
| **20 – 39** | Guarded | ALLOW (Monitored) |
| **40 – 59** | Medium | ALLOW or REQUIRE_APPROVAL based on policy |
| **60 – 79** | High | REQUIRE_APPROVAL |
| **80 – 100** | Critical | BLOCK |

---

## 4. Policy Decision Tree

```mermaid
graph TD
    Start["Intercepted Tool Invocation"] --> ActivePolicyCheck{"Does an active policy rule match?"}
    
    ActivePolicyCheck -->|Rule Type = DENY| BlockAction["Decision: BLOCK"]
    ActivePolicyCheck -->|Rule Type = REQUIRE_APPROVAL| ApprovalAction["Decision: REQUIRE_APPROVAL"]
    ActivePolicyCheck -->|No Explicit Rule| ScoreCheck{"Evaluate Risk Score"}
    
    ScoreCheck -->|Score >= AUTO_BLOCK_THRESHOLD (80)| BlockAction
    ScoreCheck -->|Score >= APPROVAL_THRESHOLD (50)| ApprovalAction
    ScoreCheck -->|Tool requires_approval flag = true| ApprovalAction
    ScoreCheck -->|Score < 50 and Safe| AllowAction["Decision: ALLOW"]
```
