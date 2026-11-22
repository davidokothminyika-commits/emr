from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import FollowUpTask
from ..schemas import FollowUpOut
from .auth import get_current_user
from ..services.audit import log_action
import uuid
from datetime import date

router = APIRouter(prefix="/api/followups", tags=["followups"])

def out(t):
    return {"id": t.id, "patient_id": t.patient_id, "description": t.description, "due_date": str(t.due_date), "priority": t.priority, "related_record_id": t.related_record_id, "status": t.status, "assigned_clinician": t.assigned_clinician}

@router.get("")
def list_followups(status: str = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(FollowUpTask)
    if status: q = q.filter(FollowUpTask.status == status)
    return [out(t) for t in q.all()]

@router.post("")
def create_followup(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = FollowUpTask(id=f"F-{uuid.uuid4().hex[:8].upper()}", patient_id=payload["patient_id"], description=payload["description"], due_date=date.fromisoformat(payload["due_date"]), priority=payload.get("priority","medium"), related_record_id=payload.get("related_record_id"), status="pending", assigned_clinician=payload.get("assigned_clinician", user.full_name if hasattr(user,'full_name') else user.username))
    db.add(t); db.commit()
    log_action(db, user.id, "followup_create", "followup", t.id)
    return out(t)

@router.patch("/{fid}")
def update_followup(fid: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(FollowUpTask).filter(FollowUpTask.id == fid).first()
    if not t: raise HTTPException(404)
    for k in ["status","description","priority"]:
        if k in payload: setattr(t, k, payload[k])
    if "due_date" in payload: t.due_date = date.fromisoformat(payload["due_date"])
    db.commit()
    log_action(db, user.id, "followup_update", "followup", fid, payload)
    return out(t)
