from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from app.database.base import Base

class SecurityAnalysis(Base):
    __tablename__ = "security_analyses"

    id = Column(String(64), primary_key=True, index=True)
    invocation_id = Column(String(64), index=True, nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False)
    risk_classification = Column(String(20), default="Low", nullable=False)
    triggered_rules = Column(JSON, default=list, nullable=False)
    evidence = Column(JSON, default=dict, nullable=False)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(String(64), primary_key=True, index=True)
    invocation_id = Column(String(64), index=True, nullable=True)
    threat_category = Column(String(50), index=True, nullable=False)  # DestructiveCommand, PromptInjection, FileTraversal, SecretExfiltration, Anomaly
    severity = Column(String(20), index=True, nullable=False)        # Low, Guarded, Medium, High, Critical
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict, nullable=False)
    affected_tool = Column(String(100), nullable=False)
    status = Column(String(20), default="NEW", index=True, nullable=False)  # NEW, INVESTIGATING, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
