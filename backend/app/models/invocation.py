from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from app.database.base import Base

class ToolInvocation(Base):
    __tablename__ = "tool_invocations"

    id = Column(String(64), primary_key=True, index=True)  # uuid
    session_id = Column(String(64), index=True, nullable=True)
    user_id = Column(String(64), index=True, nullable=True)
    server_id = Column(String(64), index=True, nullable=False)
    tool_name = Column(String(100), index=True, nullable=False)
    arguments = Column(JSON, nullable=False, default=dict)
    
    # Lifecycle & status
    status = Column(String(30), default="received", nullable=False)  # received, analyzing, pending_approval, executing, completed, blocked, failed
    risk_score = Column(Float, default=0.0, nullable=False)
    risk_classification = Column(String(20), default="Low", nullable=False)  # Low, Guarded, Medium, High, Critical
    decision = Column(String(20), default="ALLOW", nullable=False)           # ALLOW, BLOCK, REQUIRE_APPROVAL
    
    approval_status = Column(String(20), default="NOT_REQUIRED", nullable=False)  # NOT_REQUIRED, PENDING, APPROVED, REJECTED, EXPIRED
    execution_status = Column(String(20), default="NOT_EXECUTED", nullable=False) # NOT_EXECUTED, SUCCESS, ERROR, BLOCKED
    
    response_data = Column(JSON, nullable=True)
    execution_duration_ms = Column(Float, default=0.0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
