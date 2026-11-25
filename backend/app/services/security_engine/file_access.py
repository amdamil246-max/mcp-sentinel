import os
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.config import settings

class FileAccessFinding(BaseModel):
    rule_id: str
    rule_name: str
    threat_category: str = "UnauthorizedFileAccess"
    severity: str  # Critical, High, Medium
    risk_score: float
    description: str
    target_path: str

class FileAccessValidator:
    """
    Validates file system paths, detects path traversal, canonicalizes paths,
    and enforces workspace boundary restrictions.
    """

    FORBIDDEN_FILE_PATTERNS = [
        (r"(^|[/\\])\.env(\.[a-zA-Z0-9_-]+)?$", "Environment Credentials File (.env)", "Critical", 95.0),
        (r"(^|[/\\])\.git[/\\]config$", "Git Configuration / Credentials", "High", 80.0),
        (r"(^|[/\\])id_(rsa|ed25519|dsa|ecdsa)(\.pub)?$", "SSH Key Pair", "Critical", 95.0),
        (r"(^|[/\\])authorized_keys$", "SSH Authorized Keys File", "High", 85.0),
        (r"(^|[/\\])(etc|etc[/\\]shadow|etc[/\\]passwd|etc[/\\]sudoers)$", "Unix Sensitive System File", "Critical", 95.0),
        (r"windows[/\\]system32[/\\]config[/\\](sam|system|security)", "Windows SAM Registry Database", "Critical", 95.0),
        (r"\.aws[/\\]credentials$", "AWS CLI Credentials", "Critical", 95.0),
        (r"\.kube[/\\]config$", "Kubernetes Cluster Config", "Critical", 90.0),
        (r"(credentials|secrets)\.(json|yaml|yml)$", "Secret Configuration File", "High", 85.0),
    ]

    DISALLOWED_EXECUTABLE_EXTENSIONS = {".exe", ".bat", ".cmd", ".vbs", ".ps1", ".sh", ".so", ".dll"}

    def __init__(self, allowed_directories: Optional[List[str]] = None):
        self.allowed_directories = [
            os.path.realpath(d) for d in (allowed_directories or settings.ALLOWED_DIRECTORIES)
        ]

    def analyze(self, path_arg: str, operation: str = "read") -> List[FileAccessFinding]:
        findings: List[FileAccessFinding] = []
        if not path_arg or not isinstance(path_arg, str):
            return findings

        raw_path = path_arg.strip()

        # 1. Detect Path Traversal Signatures (raw and URL-decoded)
        decoded = urllib.parse.unquote(raw_path)
        if ".." in raw_path or ".." in decoded or "/../" in raw_path or "\\..\\" in raw_path:
            findings.append(FileAccessFinding(
                rule_id="FILE-TRAVERSAL-001",
                rule_name="Directory Traversal Attempt (Dot-Dot-Slash)",
                severity="Critical",
                risk_score=90.0,
                description="Detected directory traversal sequence '../' attempting to escape sandbox boundaries",
                target_path=raw_path
            ))

        # 2. Check Forbidden Sensitive System and Secret Files
        norm_path = raw_path.replace("\\", "/").lower()
        for pattern, name, severity, score in self.FORBIDDEN_FILE_PATTERNS:
            if re.search(pattern, norm_path, re.IGNORECASE):
                findings.append(FileAccessFinding(
                    rule_id=f"FILE-FORBIDDEN-{abs(hash(pattern)) % 10000:04d}",
                    rule_name=name,
                    severity=severity,
                    risk_score=score,
                    description=f"Attempted access to restricted sensitive file: {name}",
                    target_path=raw_path
                ))

        # 3. Canonical path boundary resolution
        try:
            # Resolve canonical path (handling symlinks and relative references)
            canonical_path = os.path.realpath(raw_path)
            
            # If path doesn't exist yet (e.g. write_file), check parent directory
            if not os.path.exists(canonical_path):
                canonical_path = os.path.realpath(os.path.dirname(raw_path) or ".")

            # Check if canonical path is within any allowed directory
            within_allowed = any(
                canonical_path.startswith(allowed_dir) or canonical_path == allowed_dir
                for allowed_dir in self.allowed_directories
            )

            # In development/standalone mode, if allowed_directories list is defined, enforce it
            if self.allowed_directories and not within_allowed:
                # Check if it's attempting to access system root or home directory
                user_home = os.path.realpath(os.path.expanduser("~"))
                if canonical_path.startswith(user_home) or canonical_path.startswith("/etc") or "windows\\system32" in canonical_path.lower():
                    findings.append(FileAccessFinding(
                        rule_id="FILE-BOUNDARY-ESCAPE",
                        rule_name="Workspace Boundary Escape Attempt",
                        severity="High",
                        risk_score=85.0,
                        description="Target path resolves outside permitted workspace sandbox directories",
                        target_path=raw_path
                    ))
        except Exception:
            pass

        # 4. Check dangerous executable file writing
        if operation in ("write", "create"):
            ext = os.path.splitext(raw_path)[1].lower()
            if ext in self.DISALLOWED_EXECUTABLE_EXTENSIONS:
                findings.append(FileAccessFinding(
                    rule_id="FILE-EXEC-WRITE",
                    rule_name="Executable / Script File Write Attempt",
                    severity="High",
                    risk_score=75.0,
                    description=f"Attempted to write an executable or script file ({ext}) to the filesystem",
                    target_path=raw_path
                ))

        return findings
