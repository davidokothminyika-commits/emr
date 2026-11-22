from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EncounterNote, Patient, Diagnosis, Medication, Allergy, LabResult, Encounter
from ..schemas import NoteOut
from .auth import get_current_user
from ..services.audit import log_action
import uuid, json

router = APIRouter(prefix="/api/encounters", tags=["encounters"])

def note_out(n):
    return {"id": n.id, "patient_id": n.patient_id, "content": n.content if n.edited_content is None else n.edited_content, "status": n.status, "created_at": str(n.created_at), "original_content": n.content}

@router.post("/draft")
def draft_note(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pid = payload.get("patient_id")
    obs = payload.get("observations", "")
    p = db.query(Patient).filter(Patient.id == pid).first()
    if not p: raise HTTPException(404)
    dx = db.query(Diagnosis).filter(Diagnosis.patient_id == pid).all()
    meds = db.query(Medication).filter(Medication.patient_id == pid).all()
    allg = db.query(Allergy).filter(Allergy.patient_id == pid).all()
    labs = db.query(LabResult).filter(LabResult.patient_id == pid).all()
    encs = db.query(Encounter).filter(Encounter.patient_id == pid).all()
    content = {
      "chief_complaint": obs or "",
      "history_of_presenting_illness": "",
      "relevant_medical_history": "; ".join([d.name for d in dx]),
      "current_medication_history": "; ".join([f"{m.name} {m.dosage or ''}" for m in meds if m.status == "active"]),
      "documented_allergies": "; ".join([a.allergen for a in allg]),
      "relevant_investigations": "; ".join([f"{l.test_name} {l.value} {l.unit or ''} ({l.date})" for l in labs]),
      "clinical_findings": "",
      "assessment": "",
      "plan": "",
      "follow_up": "",
      "disclaimer": "AI-generated draft. Requires review and approval by a qualified healthcare professional."
    }
    n = EncounterNote(id=f"N-{uuid.uuid4().hex[:8].upper()}", patient_id=pid, content=content, status="draft")
    db.add(n); db.commit()
    log_action(db, user.id, "note_creation", "encounter_note", n.id, {"patient_id": pid})
    return note_out(n)

@router.get("/notes")
def list_notes(patient_id: str = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(EncounterNote)
    if patient_id: q = q.filter(EncounterNote.patient_id == patient_id)
    return [note_out(n) for n in q.all()]

@router.patch("/notes/{nid}")
def edit_note(nid: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.query(EncounterNote).filter(EncounterNote.id == nid).first()
    if not n: raise HTTPException(404)
    if "content" in payload:
        n.edited_content = payload["content"]
    db.commit()
    log_action(db, user.id, "note_edit", "encounter_note", nid)
    return note_out(n)

@router.post("/notes/{nid}/approve")
def approve_note(nid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("clinician","administrator"):
        raise HTTPException(403)
    n = db.query(EncounterNote).filter(EncounterNote.id == nid).first()
    if not n: raise HTTPException(404)
    n.status = "approved"
    n.reviewer_id = user.id
    from datetime import datetime
    n.reviewed_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "note_approval", "encounter_note", nid)
    return note_out(n)

@router.post("/notes/{nid}/reject")
def reject_note(nid: str, payload: dict = {}, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.query(EncounterNote).filter(EncounterNote.id == nid).first()
    if not n: raise HTTPException(404)
    n.status = "rejected"
    n.rejection_reason = payload.get("reason", "")
    n.reviewer_id = user.id
    from datetime import datetime
    n.reviewed_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "note_rejection", "encounter_note", nid, {"reason": n.rejection_reason})
    return note_out(n)
