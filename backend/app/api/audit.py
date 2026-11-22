from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import AuditLog
from .auth import get_current_user

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("")
def list_audit(db: Session = Depends(get_db), user=Depends(get_current_user)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200).all()
    return [{"id": l.id, "user_id": l.user_id, "action": l.action, "resource_type": l.resource_type, "resource_id": l.resource_id, "timestamp": str(l.timestamp), "details": l.details} for l in logs]
