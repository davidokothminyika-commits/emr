from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Patient, Diagnosis, Medication, Allergy, LabResult, Encounter
from ..schemas import PatientOut, PatientHistory, DiagnosisOut, MedicationOut, AllergyOut, LabResultOut, EncounterOut
from ..adapters.emr import get_adapter
from ..services.audit import log_action
from .auth import get_current_user

router = APIRouter(prefix="/api/patients", tags=["patients"])

def patient_out(p):
    return PatientOut(id=p.id, name=p.name, dob=p.dob, sex=p.sex, facility_id=p.facility_id, registration_date=p.registration_date, program=p.program, status=p.status)

@router.get("")
def list_patients(q: str = "", db: Session = Depends(get_db), user=Depends(get_current_user)):
    ad = get_adapter()
    pts = ad.get_patients(db)
    if q:
        ql = q.lower()
        pts = [p for p in pts if ql in p.name.lower() or ql in p.id.lower()]
    return [patient_out(p).model_dump() for p in pts]

@router.get("/{pid}")
def get_patient(pid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ad = get_adapter()
    p = ad.get_patient(db, pid)
    if not p:
        raise HTTPException(404, "Patient not found")
    log_action(db, user.id, "patient_access", "patient", pid)
    return patient_out(p).model_dump()

@router.get("/{pid}/history")
def get_history(pid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ad = get_adapter()
    rec = ad.get_record(db, pid)
    if not rec:
        raise HTTPException(404, "Patient not found")
    log_action(db, user.id, "patient_history_access", "patient", pid)
    return {
        "patient": patient_out(rec.patient).model_dump(),
        "diagnoses": [DiagnosisOut(id=d.id, patient_id=d.patient_id, code=d.code, name=d.name, date=d.date, status=d.status, encounter_ref=d.encounter_ref, origin=d.origin).model_dump() for d in rec.diagnoses],
        "medications": [MedicationOut(id=m.id, patient_id=m.patient_id, name=m.name, dosage=m.dosage, frequency=m.frequency, start_date=m.start_date, end_date=m.end_date, status=m.status, encounter_ref=m.encounter_ref, origin=m.origin).model_dump() for m in rec.medications],
        "allergies": [AllergyOut(id=a.id, patient_id=a.patient_id, allergen=a.allergen, reaction=a.reaction, severity=a.severity, date=a.date, encounter_ref=a.encounter_ref, origin=a.origin).model_dump() for a in rec.allergies],
        "labs": [LabResultOut(id=l.id, patient_id=l.patient_id, test_name=l.test_name, value=l.value, unit=l.unit, date=l.date, reference_range=l.reference_range, encounter_ref=l.encounter_ref, origin=l.origin).model_dump() for l in rec.labs],
        "encounters": [EncounterOut(id=e.id, patient_id=e.patient_id, date=e.date, type=e.type, notes=e.notes, clinician=e.clinician, complete=e.complete, origin=e.origin).model_dump() for e in rec.encounters],
    }

@router.get("/{pid}/summary")
def get_summary_placeholder(pid: str):
    return {"message": "Use POST generate-summary"}
