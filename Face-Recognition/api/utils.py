import secrets
from datetime import datetime, timedelta
from config import SESSION_TIMEOUT_HOURS

def generate_session_id() -> str:
    """Generate random session ID"""
    return secrets.token_urlsafe(32)

def get_session_expiry() -> datetime:
    """Get session expiry time"""
    return datetime.utcnow() + timedelta(hours=SESSION_TIMEOUT_HOURS)

