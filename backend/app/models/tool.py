from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class RegisteredTool(Base):
    __tablename__ = "registered_tools"

    id = Column(String(100), primary_key=True, index=True)  # e.g., "server-01:run_command"
    server_id = Column(String(64), ForeignKey("mcp_servers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    input_schema = Column(JSON, nullable=True, default=dict)
    permission_level = Column(String(20), default="execute", nullable=False)  # read, write, execute, admin
    trust_level = Column(String(20), default="untrusted", nullable=False)      # trusted, monitored, untrusted, blocked
    is_enabled = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    server = relationship("MCPServer", back_populates="tools")
