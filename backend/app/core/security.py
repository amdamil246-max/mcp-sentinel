import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import jwt
from app.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None

def compute_arguments_hash(args: Dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 hash of tool invocation arguments."""
    normalized = json.dumps(args, sort_keys=True, separators=(',', ':'), default=str)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def compute_audit_hash(previous_hash: Optional[str], event_type: str, actor: str, action: str, details: Dict[str, Any], timestamp: Any) -> str:
    """Computes tamper-evident SHA-256 chaining hash for audit logs."""
    ts_str = timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp)
    data = {
        "prev": previous_hash or "GENESIS",
        "type": event_type,
        "actor": actor,
        "action": action,
        "details": details,
        "ts": ts_str[:19]
    }
    normalized = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
