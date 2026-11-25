from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(String(64), primary_key=True, index=True)  # e.g., "terminal-server-01"
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    connection_type = Column(String(20), nullable=False, default="stdio")  # stdio, sse, streamable_http
    command = Column(String(255), nullable=True)
    args = Column(JSON, nullable=True, default=list)
    env = Column(JSON, nullable=True, default=dict)
    url = Column(String(255), nullable=True)
    headers = Column(JSON, nullable=True, default=dict)
    is_enabled = Column(Boolean, default=True, nullable=False)
    health_status = Column(String(20), default="healthy", nullable=False)  # healthy, degraded, offline
    last_connected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tools = relationship("RegisteredTool", back_populates="server", cascade="all, delete-orphan")
