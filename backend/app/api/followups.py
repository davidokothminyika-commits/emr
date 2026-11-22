from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import FollowUpTask, Patient, User
from .auth import get_current_user
from ..services.audit import log_action
import uuid
from datetime import date, datetime

router = APIRouter(prefix="/api/followups", tags=["followups"])

def out(t):
    overdue = t.status == "pending" and t.due_date < date.today()
    status = "overdue" if overdue else t.status
    return {
        "id": t.id, "patient_id": t.patient_id, "title": t.title, "description": t.description,
        "due_date": str(t.due_date), "priority": t.priority, "status": status, "raw_status": t.status,
        "assigned_clinician_id": t.assigned_clinician_id, "assigned_clinician": t.assigned_clinician,
        "related_record_type": t.related_record_type, "related_record_id": t.related_record_id,
        "completion_notes": t.completion_notes, "created_by": t.created_by,
        "created_at": str(t.created_at), "updated_at": str(t.updated_at),
        "completed_at": str(t.completed_at) if t.completed_at else None,
        "cancelled_at": str(t.cancelled_at) if t.cancelled_at else None,
    }

@router.get("")
def list_followups(status: str = None, patient_id: str = None, priority: str = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(FollowUpTask)
    if patient_id: q = q.filter(FollowUpTask.patient_id == patient_id)
    if priority: q = q.filter(FollowUpTask.priority == priority)
    items = q.all()
    if status:
        filtered = []
        for t in items:
            s = "overdue" if (t.status == "pending" and t.due_date < date.today()) else t.status
            if s == status:
                filtered.append(t)
        items = filtered
    return [out(t) for t in items]

@router.get("/{fid}")
def get_followup(fid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(FollowUpTask).filter(FollowUpTask.id == fid).first()
    if not t: raise HTTPException(404)
    return out(t)

@router.post("")
def create_followup(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pid = payload.get("patient_id")
    p = db.query(Patient).filter(Patient.id == pid).first()
    if not p: raise HTTPException(400, "Invalid patient")
    if not payload.get("title") and not payload.get("description"):
        raise HTTPException(400, "Title or description required")
    due = date.fromisoformat(payload["due_date"])
    t = FollowUpTask(
        id=f"FU-{uuid.uuid4().hex[:8].upper()}",
        patient_id=pid,
        title=payload.get("title"),
        description=payload.get("description", ""),
        due_date=due,
        priority=payload.get("priority", "medium"),
        status="pending",
        assigned_clinician_id=payload.get("assigned_clinician_id"),
        assigned_clinician=payload.get("assigned_clinician", user.full_name),
        related_record_type=payload.get("related_record_type"),
        related_record_id=payload.get("related_record_id"),
        created_by=user.id,
    )
    db.add(t); db.commit()
    log_action(db, user.id, "followup_create", "followup", t.id, {"patient_id": pid})
    return out(t)

@router.patch("/{fid}")
def update_followup(fid: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(FollowUpTask).filter(FollowUpTask.id == fid).first()
    if not t: raise HTTPException(404)
    prev = {"priority": t.priority, "due_date": str(t.due_date), "assigned_clinician": t.assigned_clinician}
    if "title" in payload: t.title = payload["title"]
    if "description" in payload: t.description = payload["description"]
    if "priority" in payload: t.priority = payload["priority"]
    if "due_date" in payload: t.due_date = date.fromisoformat(payload["due_date"])
    if "assigned_clinician" in payload: t.assigned_clinician = payload["assigned_clinician"]
    if "assigned_clinician_id" in payload: t.assigned_clinician_id = payload["assigned_clinician_id"]
    if "related_record_type" in payload: t.related_record_type = payload["related_record_type"]
    if "related_record_id" in payload: t.related_record_id = payload["related_record_id"]
    t.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "followup_edit", "followup", fid, {"previous": prev, "new": payload})
    return out(t)

@router.patch("/{fid}/complete")
def complete_followup(fid: str, payload: dict = {}, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(FollowUpTask).filter(FollowUpTask.id == fid).first()
    if not t: raise HTTPException(404)
    t.status = "completed"
    t.completion_notes = payload.get("notes")
    t.completed_at = datetime.utcnow()
    t.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "followup_complete", "followup", fid, {"notes": payload.get("notes")})
    return out(t)

@router.patch("/{fid}/cancel")
def cancel_followup(fid: str, payload: dict = {}, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(FollowUpTask).filter(FollowUpTask.id == fid).first()
    if not t: raise HTTPException(404)
    t.status = "cancelled"
    t.cancelled_at = datetime.utcnow()
    t.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "followup_cancel", "followup", fid, {"reason": payload.get("reason")})
    return out(t)

@router.patch("/{fid}/reopen")
def reopen_followup(fid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(FollowUpTask).filter(FollowUpTask.id == fid).first()
    if not t: raise HTTPException(404)
    t.status = "pending"
    t.completed_at = None
    t.cancelled_at = None
    t.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "followup_reopen", "followup", fid)
    return out(t)
