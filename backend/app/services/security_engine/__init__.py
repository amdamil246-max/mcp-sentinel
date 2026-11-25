from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.security_engine.command_analyzer import CommandAnalyzer, CommandFinding
from app.services.security_engine.prompt_injection import PromptInjectionDetector, PromptInjectionFinding
from app.services.security_engine.sensitive_data import SensitiveDataDetector, SecretFinding
from app.services.security_engine.file_access import FileAccessValidator, FileAccessFinding
from app.services.security_engine.behavioral import BehavioralAnomalyDetector, behavioral_detector

class ComprehensiveSecurityResult(BaseModel):
    findings: List[Dict[str, Any]]
    max_risk_score: float
    has_critical_findings: bool
    categories_detected: List[str]
    evidence: Dict[str, Any]

class SecurityEngine:
    """
    Unified Security Analysis Engine.
    Executes all detection modules deterministically across tool calls, arguments, and context.
    """

    def __init__(self):
        self.cmd_analyzer = CommandAnalyzer()
        self.pi_detector = PromptInjectionDetector()
        self.secret_detector = SensitiveDataDetector()
        self.file_validator = FileAccessValidator()
        self.behavior_detector = behavioral_detector

    def inspect_request(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> ComprehensiveSecurityResult:
        all_findings: List[Dict[str, Any]] = []
        evidence: Dict[str, Any] = {}
        max_score: float = 0.0

        # 1. Behavioral check
        if session_id:
            behavior_findings = self.behavior_detector.analyze(session_id, tool_name)
            for bf in behavior_findings:
                finding_dict = bf.model_dump()
                all_findings.append(finding_dict)
                max_score = max(max_score, bf.risk_score)
            if behavior_findings:
                evidence["behavioral"] = [bf.model_dump() for bf in behavior_findings]

        # 2. Sensitive data / secret exposure check in arguments
        secret_findings = self.secret_detector.analyze(arguments)
        for sf in secret_findings:
            finding_dict = sf.model_dump()
            all_findings.append(finding_dict)
            max_score = max(max_score, sf.risk_score)
        if secret_findings:
            evidence["sensitive_data"] = [sf.model_dump() for sf in secret_findings]

        # 3. Prompt injection in arguments
        pi_findings = self.pi_detector.analyze(arguments)
        for pf in pi_findings:
            finding_dict = pf.model_dump()
            all_findings.append(finding_dict)
            max_score = max(max_score, pf.risk_score)
        if pi_findings:
            evidence["prompt_injection"] = [pf.model_dump() for pf in pi_findings]

        # 4. Command analysis (if tool is run_command, exec, terminal, bash, powershell, or has cmd/command arg)
        is_cmd_tool = any(k in tool_name.lower() for k in ["command", "terminal", "bash", "sh", "exec", "powershell"])
        cmd_arg = arguments.get("command") or arguments.get("cmd") or arguments.get("script") or arguments.get("input")
        if (is_cmd_tool or cmd_arg) and isinstance(cmd_arg, str):
            cmd_findings = self.cmd_analyzer.analyze(cmd_arg)
            for cf in cmd_findings:
                finding_dict = cf.model_dump()
                all_findings.append(finding_dict)
                max_score = max(max_score, cf.risk_score)
            if cmd_findings:
                evidence["command_analysis"] = [cf.model_dump() for cf in cmd_findings]

        # 5. File access validation (if tool is file-related or has path/file/dir argument)
        is_file_tool = any(k in tool_name.lower() for k in ["file", "dir", "path", "read", "write", "delete", "list"])
        path_arg = arguments.get("path") or arguments.get("file_path") or arguments.get("filepath") or arguments.get("directory")
        operation = "write" if any(w in tool_name.lower() for w in ["write", "create", "append", "delete"]) else "read"
        if (is_file_tool or path_arg) and isinstance(path_arg, str):
            file_findings = self.file_validator.analyze(path_arg, operation=operation)
            for ff in file_findings:
                finding_dict = ff.model_dump()
                all_findings.append(finding_dict)
                max_score = max(max_score, ff.risk_score)
            if file_findings:
                evidence["file_access"] = [ff.model_dump() for ff in file_findings]

        # Identify unique threat categories
        categories = list(set(f.get("threat_category", "Unknown") for f in all_findings))
        has_critical = any(f.get("severity") == "Critical" or f.get("risk_score", 0) >= 80.0 for f in all_findings)

        return ComprehensiveSecurityResult(
            findings=all_findings,
            max_risk_score=max_score,
            has_critical_findings=has_critical,
            categories_detected=categories,
            evidence=evidence
        )

    def inspect_response(self, response_data: Any) -> ComprehensiveSecurityResult:
        """Inspects MCP tool outputs/responses before sending them back to the AI Agent."""
        all_findings: List[Dict[str, Any]] = []
        evidence: Dict[str, Any] = {}
        max_score: float = 0.0

        # Check for secrets leaked in tool output
        secret_findings = self.secret_detector.analyze(response_data)
        for sf in secret_findings:
            finding_dict = sf.model_dump()
            all_findings.append(finding_dict)
            max_score = max(max_score, sf.risk_score)
        if secret_findings:
            evidence["sensitive_data"] = [sf.model_dump() for sf in secret_findings]

        # Check for prompt injection payloads returned by external tools/webpages
        pi_findings = self.pi_detector.analyze(response_data)
        for pf in pi_findings:
            finding_dict = pf.model_dump()
            all_findings.append(finding_dict)
            max_score = max(max_score, pf.risk_score)
        if pi_findings:
            evidence["prompt_injection"] = [pf.model_dump() for pf in pi_findings]

        categories = list(set(f.get("threat_category", "Unknown") for f in all_findings))
        has_critical = any(f.get("severity") == "Critical" or f.get("risk_score", 0) >= 80.0 for f in all_findings)

        return ComprehensiveSecurityResult(
            findings=all_findings,
            max_risk_score=max_score,
            has_critical_findings=has_critical,
            categories_detected=categories,
            evidence=evidence
        )

security_engine = SecurityEngine()
