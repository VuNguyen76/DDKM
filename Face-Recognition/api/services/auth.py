from sqlalchemy.orm import Session
from datetime import datetime
from models import Session as DBSession, ADMIN_USERNAME, ADMIN_PASSWORD
from utils import generate_session_id, get_session_expiry

def authenticate_user(db: Session, username: str, password: str):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return None

    session_id = generate_session_id()
    session = DBSession(
        session_id=session_id,
        username=username,
        expires_at=get_session_expiry()
    )
    db.add(session)
    db.commit()

    return session_id

def get_session(db: Session, session_id: str):
    session = db.query(DBSession).filter(
        DBSession.session_id == session_id,
        DBSession.expires_at > datetime.utcnow()
    ).first()
    return session

def logout_user(db: Session, session_id: str):
    session = db.query(DBSession).filter(DBSession.session_id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False
