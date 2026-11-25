import os
from typing import List, Optional
from pydantic import BaseModel

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "sentinel.db").replace("\\", "/")

class Settings(BaseModel):
    PROJECT_NAME: str = "MCP Sentinel"
    PROJECT_TAGLINE: str = "Your Security Firewall for AI Agents"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mcp-sentinel-ultra-secure-secret-key-32chars-minimum-required")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database (PostgreSQL with SQLite fallback)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    
    # Redis configuration (optional distributed coordination)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    
    # Gateway settings
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))
    GATEWAY_APPROVAL_EXPIRATION_SECONDS: int = 300  # 5 minutes
    
    # Risk Scoring Thresholds
    RISK_THRESHOLD_LOW_MAX: int = 19
    RISK_THRESHOLD_GUARDED_MAX: int = 39
    RISK_THRESHOLD_MEDIUM_MAX: int = 59
    RISK_THRESHOLD_HIGH_MAX: int = 79
    RISK_THRESHOLD_CRITICAL_MIN: int = 80
    
    # Policy defaults
    APPROVAL_REQUIRED_SCORE_THRESHOLD: int = 50
    AUTO_BLOCK_SCORE_THRESHOLD: int = 80
    
    # AI Security Analyst
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
    AI_API_KEY: Optional[str] = os.getenv("AI_API_KEY", None)
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-1.5-pro")

    # Allowed workspace roots for file operations
    ALLOWED_DIRECTORIES: List[str] = [
        os.path.join(BASE_DIR, "workspace"),
        os.path.join(BASE_DIR, "scratch"),
        os.path.join(BASE_DIR, "sandbox")
    ]

settings = Settings()
