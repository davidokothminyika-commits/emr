from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import GeneratedSummary, ClinicalAlert
from ..schemas import SummaryOut
from ..services.summarizer import normalize_record, generate_summary_llm, validate_summary
from ..services.audit import log_action
from .auth import get_current_user
import uuid

router = APIRouter(tags=["intelligence"])

@router.post("/api/patients/{pid}/generate-summary")
def generate_summary(pid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rec = normalize_record(db, pid)
    if not rec.get("patient"):
        raise HTTPException(404, "Patient not found")
    summary = generate_summary_llm(rec)
    ok, errors = validate_summary(summary, rec)
    if not ok:
        summary.setdefault("items_for_clinician_review", []).extend(errors)
    gs = GeneratedSummary(id=f"S-{uuid.uuid4().hex[:8].upper()}", patient_id=pid, content=summary, status="draft")
    db.add(gs)
    db.commit()
    log_action(db, user.id, "summary_generation", "summary", gs.id, {"patient_id": pid})
    return {"id": gs.id, "patient_id": pid, "content": summary, "status": gs.status, "version": gs.version, "created_at": str(gs.created_at)}

@router.get("/api/patients/{pid}/timeline")
def timeline(pid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from ..models import Medication, LabResult, Encounter, Diagnosis
    meds = db.query(Medication).filter(Medication.patient_id == pid).all()
    labs = db.query(LabResult).filter(LabResult.patient_id == pid).all()
    encs = db.query(Encounter).filter(Encounter.patient_id == pid).all()
    dxs = db.query(Diagnosis).filter(Diagnosis.patient_id == pid).all()
    events = []
    for m in meds:
        events.append({"date": str(m.start_date), "type": "medication", "title": f"Start {m.name}", "source_id": m.id})
        if m.end_date:
            events.append({"date": str(m.end_date), "type": "medication", "title": f"End {m.name}", "source_id": m.id})
    for l in labs:
        events.append({"date": str(l.date), "type": "lab", "title": f"{l.test_name}: {l.value} {l.unit or ''}", "source_id": l.id})
    for e in encs:
        events.append({"date": str(e.date), "type": "encounter", "title": f"{e.type}", "source_id": e.id})
    for d in dxs:
        events.append({"date": str(d.date), "type": "diagnosis", "title": f"{d.name}", "source_id": d.id})
    events.sort(key=lambda x: x["date"])
    return events

@router.get("/api/patients/{pid}/alerts")
def patient_alerts(pid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    alerts = db.query(ClinicalAlert).filter(ClinicalAlert.patient_id == pid).all()
    return [alert_out(a) for a in alerts]

def alert_out(a):
    from ..schemas import AlertOut
    return AlertOut(id=a.id, patient_id=a.patient_id, rule_id=a.rule_id, title=a.title, severity=a.severity, reason=a.reason, trigger_date=a.trigger_date, source_ids=a.source_ids or [], evidence_dates=a.evidence_dates or [], recommended_action=a.recommended_action, status=a.status, dismissed_reason=a.dismissed_reason).model_dump()
