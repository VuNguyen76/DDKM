from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from pydantic import BaseModel
from services.auth import authenticate_user, get_session, logout_user
from models import ADMIN_USERNAME

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    session_id: str
    username: str

def require_admin(auth_session_id: str = Header(None, alias="session-id"), db: Session = Depends(get_db)):
    if not auth_session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    session = get_session(db, auth_session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return session

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    session_id = authenticate_user(db, request.username, request.password)
    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "session_id": session_id,
        "username": ADMIN_USERNAME
    }

@router.post("/logout")
def logout(session_id: str = Header(None, alias="session-id"), db: Session = Depends(get_db)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    success = logout_user(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Logged out successfully"}
