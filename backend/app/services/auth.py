import hashlib
from sqlalchemy.orm import Session
from ..models import User
from ..schemas import UserOut

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def authenticate(db: Session, username: str, password: str):
    u = db.query(User).filter(User.username == username).first()
    if u and u.password_hash == hash_pw(password):
        return u
    return None
def to_out(u):
    return UserOut(id=u.id, username=u.username, full_name=u.full_name, role=u.role)
