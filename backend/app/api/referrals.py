from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Referral, Patient, Diagnosis, Medication, Allergy, LabResult, Encounter
from .auth import get_current_user
from ..services.audit import log_action
import uuid

router = APIRouter(prefix="/api/referrals", tags=["referrals"])

def out(r):
    return {"id": r.id, "patient_id": r.patient_id, "content": r.content, "status": r.status, "created_at": str(r.created_at)}

@router.post("/generate")
def generate_referral(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pid = payload["patient_id"]
    p = db.query(Patient).filter(Patient.id == pid).first()
    if not p: raise HTTPException(404)
    dx = db.query(Diagnosis).filter(Diagnosis.patient_id == pid).all()
    meds = db.query(Medication).filter(Medication.patient_id == pid).all()
    allg = db.query(Allergy).filter(Allergy.patient_id == pid).all()
    labs = db.query(LabResult).filter(LabResult.patient_id == pid).all()
    encs = db.query(Encounter).filter(Encounter.patient_id == pid).all()
    content = {
      "patient_identification": {"id": p.id, "name": p.name, "dob": str(p.dob), "sex": p.sex},
      "referral_reason": payload.get("reason",""),
      "relevant_diagnoses": [d.name for d in dx],
      "relevant_medical_history": [e.notes for e in encs if e.notes],
      "current_medications": [f"{m.name} {m.dosage or ''}" for m in meds if m.status=="active"],
      "allergies": [a.allergen for a in allg],
      "relevant_labs": [f"{l.test_name}: {l.value} {l.unit or ''} ({l.date})" for l in labs],
      "previous_encounters": [f"{e.type} on {e.date}" for e in encs],
      "outstanding_investigations": [],
      "referring_clinician": user.full_name,
      "referral_destination": payload.get("destination",""),
      "date": str(__import__("datetime").date.today()),
      "disclaimer": "AI-generated draft. Requires review and approval."
    }
    r = Referral(id=f"R-{uuid.uuid4().hex[:8].upper()}", patient_id=pid, content=content, status="draft")
    db.add(r); db.commit()
    log_action(db, user.id, "referral_generation", "referral", r.id, {"patient_id": pid})
    return out(r)

@router.get("")
def list_referrals(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [out(r) for r in db.query(Referral).all()]
