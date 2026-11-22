from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import LabResult, Patient
from ..schemas import LabResultOut
from .auth import get_current_user

router = APIRouter(tags=["laboratory"])

@router.get("/api/patients/{pid}/laboratory")
def patient_labs(pid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    labs = db.query(LabResult).filter(LabResult.patient_id == pid).order_by(LabResult.date.desc()).all()
    return [LabResultOut(id=l.id, patient_id=l.patient_id, test_name=l.test_name, value=l.value, unit=l.unit, date=l.date, reference_range=l.reference_range, encounter_ref=l.encounter_ref, origin=l.origin).model_dump() for l in labs]

@router.get("/api/laboratory")
def all_labs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    labs = db.query(LabResult).order_by(LabResult.date.desc()).all()
    return [LabResultOut(id=l.id, patient_id=l.patient_id, test_name=l.test_name, value=l.value, unit=l.unit, date=l.date, reference_range=l.reference_range, encounter_ref=l.encounter_ref, origin=l.origin).model_dump() for l in labs]
