from sqlalchemy.orm import Session
from ..models import AuditLog
import uuid

def log_action(db: Session, user_id: str, action: str, resource_type: str, resource_id: str = None, details: dict = None):
    db.add(AuditLog(id=f"AL-{uuid.uuid4().hex[:8].upper()}", user_id=user_id, action=action, resource_type=resource_type, resource_id=resource_id, details=details or {}))
    db.commit()
