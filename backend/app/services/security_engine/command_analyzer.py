import re
import shlex
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class CommandFinding(BaseModel):
    rule_id: str
    rule_name: str
    threat_category: str
    severity: str  # Critical, High, Medium, Guarded, Low
    risk_score: float
    description: str
    matched_pattern: str
    command_snippet: str

class CommandAnalyzer:
    """
    Advanced security analyzer for terminal and shell commands.
    Parses commands, shell operators, dangerous arguments, and known attack patterns.
    """

    # Highly dangerous / destructive command patterns
    CRITICAL_PATTERNS = [
        (r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\s+[/~*]", "Destructive Recursive Deletion", "DestructiveCommand", 95.0),
        (r"\brmdir\s+/[sS]\s+/[qQ]\s+[cC]:\\", "Windows Recursive Disk Deletion", "DestructiveCommand", 95.0),
        (r"\bdel\s+/[fF]\s+/[sS]\s+/[qQ]\s+[cC]:\\", "Windows Force Delete All", "DestructiveCommand", 95.0),
        (r"\bmkfs(\.[a-z0-9]+)?\s+", "Filesystem Format Attempt", "DestructiveCommand", 95.0),
        (r"\bdd\s+if=.*\s+of=/dev/[sh]d[a-z]", "Raw Disk Overwrite", "DestructiveCommand", 95.0),
        (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "Fork Bomb Attack", "DenialOfService", 95.0),
        (r"\bformat\s+[c-zC-Z]:\s+/[fF][sS]:", "Windows Format Volume", "DestructiveCommand", 95.0),
    ]

    # Reverse shell & Exfiltration patterns
    REVERSE_SHELL_PATTERNS = [
        (r"\bnc(\.traditional)?\s+-[ecl]\s+.*\b(sh|bash|cmd|powershell)\b", "Netcat Reverse Shell", "ReverseShell", 90.0),
        (r"/dev/tcp/[0-9a-zA-Z\.\-]+/[0-9]+", "Bash /dev/tcp Socket Redirection", "ReverseShell", 90.0),
        (r"bash\s+-i\s+>&?\s*/dev/tcp/", "Interactive Bash Reverse Shell", "ReverseShell", 95.0),
        (r"python(\d)?\s+-c\s+.*socket.*subprocess.*pty", "Python Reverse Shell One-Liner", "ReverseShell", 90.0),
        (r"powershell(\.exe)?\s+.*New-Object\s+Net\.Sockets\.TCPClient", "PowerShell TCP Client Reverse Shell", "ReverseShell", 90.0),
        (r"\bmkfifo\s+/tmp/.*\bsh\b", "Named Pipe Reverse Shell", "ReverseShell", 85.0),
    ]

    # Download and Execute patterns
    DOWNLOAD_EXEC_PATTERNS = [
        (r"(curl|wget)\s+.*\|\s*(bash|sh|zsh|python|perl)", "Download and Execute Pipeline", "RemoteExecution", 88.0),
        (r"powershell(\.exe)?\s+.*(Invoke-Expression|IEX)\s*\(?\s*(New-Object\s+Net\.WebClient|Invoke-WebRequest|iwr)", "PowerShell In-Memory Download-Execute", "RemoteExecution", 90.0),
        (r"curl\s+-s.*\s+-\bO\b.*\s*&&\s*chmod\s+\+x.*\s*&&\s*\./", "Download Staging and Execute", "RemoteExecution", 85.0),
        (r"certutil(\.exe)?\s+-urlcache\s+-split\s+-f", "Certutil Remote File Staging", "RemoteExecution", 80.0),
    ]

    # Privilege Escalation & Security Disabling
    PRIVILEGE_ESCALATION_PATTERNS = [
        (r"\bchmod\s+(-R\s+)?777\s+/", "Insecure World-Writable Permission Assignment", "PrivilegeEscalation", 85.0),
        (r"\bchown\s+-R\s+root\s+", "Ownership Escalation to Root", "PrivilegeEscalation", 80.0),
        (r"\bsudo\s+su\s+-?", "Root Shell Escalation", "PrivilegeEscalation", 75.0),
        (r"\bSet-ExecutionPolicy\s+(Bypass|Unrestricted)", "PowerShell Security Policy Bypass", "PrivilegeEscalation", 80.0),
        (r"\b(ufw\s+disable|iptables\s+-F)", "Host Firewall Disabling", "DefenseEvasion", 85.0),
        (r"\bnetsh\s+advfirewall\s+set\s+allprofiles\s+state\s+off", "Windows Firewall Disabling", "DefenseEvasion", 85.0),
        (r"\bsetenforce\s+0", "SELinux Disabling", "DefenseEvasion", 80.0),
    ]

    # Credential Harvesting & Sensitive System File Access
    CREDENTIAL_ACCESS_PATTERNS = [
        (r"(cat|type|more|less|tail|head)\s+.*(/etc/shadow|/etc/gshadow)", "Shadow Password File Reading", "CredentialTheft", 90.0),
        (r"\breg\s+save\s+hklm\\(sam|system|security)", "Windows Registry Hive Dumping", "CredentialTheft", 92.0),
        (r"\bmimikatz", "Mimikatz Credential Dumper Tool", "CredentialTheft", 95.0),
        (r"security\s+dump-keychain", "macOS Keychain Credential Extraction", "CredentialTheft", 90.0),
        (r"\bcat\s+~?/\.ssh/id_[a-zA-Z0-9_-]+", "SSH Private Key Exfiltration Attempt", "CredentialTheft", 85.0),
    ]

    # Network Scanning & Reconnaissance
    NETWORK_RECON_PATTERNS = [
        (r"\bnmap\s+(-[a-zA-Z0-9]+\s+)*", "Port Scanning via Nmap", "NetworkRecon", 60.0),
        (r"\bmasscan\s+", "High-rate Network Port Scanner", "NetworkRecon", 65.0),
        (r"\barp-scan\s+", "Local Network ARP Enumeration", "NetworkRecon", 55.0),
    ]

    def analyze(self, command: str) -> List[CommandFinding]:
        findings: List[CommandFinding] = []
        if not command or not isinstance(command, str):
            return findings

        cmd_clean = command.strip()

        # Check all pattern rule categories
        all_rules = (
            self.CRITICAL_PATTERNS
            + self.REVERSE_SHELL_PATTERNS
            + self.DOWNLOAD_EXEC_PATTERNS
            + self.PRIVILEGE_ESCALATION_PATTERNS
            + self.CREDENTIAL_ACCESS_PATTERNS
            + self.NETWORK_RECON_PATTERNS
        )

        for pattern, rule_name, category, score in all_rules:
            match = re.search(pattern, cmd_clean, re.IGNORECASE)
            if match:
                severity = "Critical" if score >= 80 else "High" if score >= 60 else "Medium"
                findings.append(CommandFinding(
                    rule_id=f"CMD-{category.upper()}-{abs(hash(pattern)) % 10000:04d}",
                    rule_name=rule_name,
                    threat_category=category,
                    severity=severity,
                    risk_score=score,
                    description=f"Detected suspicious command pattern: {rule_name}",
                    matched_pattern=pattern,
                    command_snippet=match.group(0)
                ))

        # Check shell operator chaining density (abuse of `;`, `&&`, `||`, `|`, backticks, `$()`)
        operators = re.findall(r"(&&|\|\||;|\||`|\$\()", cmd_clean)
        if len(operators) >= 4:
            findings.append(CommandFinding(
                rule_id="CMD-CHAINING-001",
                rule_name="Excessive Shell Command Chaining",
                threat_category="CommandObfuscation",
                severity="Guarded",
                risk_score=35.0,
                description=f"Command contains {len(operators)} chained operators, possibly concealing malicious payloads",
                matched_pattern="operators_count",
                command_snippet=cmd_clean[:60] + "..." if len(cmd_clean) > 60 else cmd_clean
            ))

        return findings
