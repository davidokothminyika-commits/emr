from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.auth import authenticate, to_out, hash_pw
from ..models import User
from ..schemas import LoginRequest, UserOut
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])
SESSIONS = {}

def get_current_user(token: str = None, authorization: str = Header(None), db: Session = Depends(get_db)):
    t = token
    if authorization and authorization.lower().startswith("bearer "):
        t = authorization.split(" ", 1)[1]
    uid = SESSIONS.get(t)
    if not uid:
        raise HTTPException(401, "Not authenticated")
    u = db.query(User).filter(User.id == uid).first()
    if not u:
        raise HTTPException(401, "Not authenticated")
    return u

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    u = authenticate(db, req.username, req.password)
    if not u:
        raise HTTPException(401, "Invalid credentials")
    token = uuid.uuid4().hex
    SESSIONS[token] = u.id
    return {"token": token, "user": to_out(u).model_dump()}

@router.post("/logout")
def logout(token: str = None):
    if token in SESSIONS:
        del SESSIONS[token]
    return {"ok": True}

@router.get("/me")
def me(token: str, db: Session = Depends(get_db)):
    uid = SESSIONS.get(token)
    if not uid:
        raise HTTPException(401, "Not authenticated")
    u = db.query(User).filter(User.id == uid).first()
    return to_out(u).model_dump()
