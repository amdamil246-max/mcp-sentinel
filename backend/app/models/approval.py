from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Text
from app.database.base import Base

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String(64), primary_key=True, index=True)
    invocation_id = Column(String(64), unique=True, index=True, nullable=False)
    tool_name = Column(String(100), nullable=False)
    server_name = Column(String(100), nullable=False)
    arguments_hash = Column(String(64), nullable=False)  # SHA-256 to prevent argument tampering
    redacted_arguments = Column(JSON, nullable=False, default=dict)
    risk_score = Column(Float, nullable=False)
    reasons = Column(JSON, nullable=False, default=list)
    requested_by = Column(String(100), nullable=True)
    
    status = Column(String(20), default="PENDING", index=True, nullable=False)  # PENDING, APPROVED, REJECTED, EXPIRED, CANCELLED
    decided_by = Column(String(100), nullable=True)
    decision_reason = Column(Text, nullable=True)
    
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)
