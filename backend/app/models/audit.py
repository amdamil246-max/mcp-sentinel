from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from app.database.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    event_type = Column(String(50), index=True, nullable=False)  # TOOL_INVOCATION, POLICY_CHANGE, APPROVAL_DECISION, AUTH_EVENT, ALERT_STATUS
    actor = Column(String(100), index=True, nullable=False)
    target_resource = Column(String(100), index=True, nullable=False)
    action = Column(String(50), nullable=False)  # ALLOWED, BLOCKED, APPROVED, REJECTED, MODIFIED, CREATED
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(45), nullable=True)
    
    # Cryptographic tamper-evident hash chaining
    previous_hash = Column(String(64), nullable=True)
    entry_hash = Column(String(64), nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
