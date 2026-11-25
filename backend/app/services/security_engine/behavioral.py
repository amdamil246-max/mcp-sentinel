import time
from collections import defaultdict, deque
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class BehavioralFinding(BaseModel):
    rule_id: str
    rule_name: str
    threat_category: str = "BehavioralAnomaly"
    severity: str  # High, Medium, Guarded
    risk_score: float
    description: str
    session_id: str

class BehavioralAnomalyDetector:
    """
    Tracks sliding-window tool invocation metrics per session/agent.
    Detects velocity bursts, brute force probing, and anomalous failure spikes.
    """

    def __init__(
        self,
        window_seconds: int = 60,
        burst_threshold: int = 25,
        consecutive_failure_threshold: int = 3
    ):
        self.window_seconds = window_seconds
        self.burst_threshold = burst_threshold
        self.consecutive_failure_threshold = consecutive_failure_threshold
        
        # session_id -> deque of timestamps
        self._invocation_history: Dict[str, deque] = defaultdict(deque)
        # session_id -> recent consecutive block count
        self._consecutive_blocks: Dict[str, int] = defaultdict(int)

    def record_decision(self, session_id: str, decision: str):
        if decision == "BLOCK":
            self._consecutive_blocks[session_id] += 1
        else:
            self._consecutive_blocks[session_id] = 0

    def analyze(self, session_id: str, tool_name: str) -> List[BehavioralFinding]:
        findings: List[BehavioralFinding] = []
        if not session_id:
            return findings

        now = time.time()
        history = self._invocation_history[session_id]

        # Prune invocations older than window
        while history and history[0] < now - self.window_seconds:
            history.popleft()

        # Add current invocation
        history.append(now)

        # 1. Velocity Burst Anomaly
        if len(history) > self.burst_threshold:
            findings.append(BehavioralFinding(
                rule_id="BEHAVIOR-BURST-001",
                rule_name="Abnormal Tool Invocation Velocity",
                severity="High",
                risk_score=70.0,
                description=f"Session generated {len(history)} tool calls in {self.window_seconds}s (threshold: {self.burst_threshold})",
                session_id=session_id
            ))

        # 2. Consecutive Block / Probing Anomaly
        block_count = self._consecutive_blocks.get(session_id, 0)
        if block_count >= self.consecutive_failure_threshold:
            findings.append(BehavioralFinding(
                rule_id="BEHAVIOR-PROBING-002",
                rule_name="Repeated Security Policy Violations (Probing Attack)",
                severity="Critical" if block_count >= 5 else "High",
                risk_score=85.0 if block_count >= 5 else 65.0,
                description=f"Session has accumulated {block_count} consecutive blocked operations, indicating potential exploit probing",
                session_id=session_id
            ))

        return findings

behavioral_detector = BehavioralAnomalyDetector()
