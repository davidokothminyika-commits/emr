from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Patient, ClinicalAlert, GeneratedSummary, EncounterNote, FollowUpTask, LabResult
from .auth import get_current_user
from datetime import date

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    patients = db.query(Patient).all()
    alerts = db.query(ClinicalAlert).all()
    notes = db.query(EncounterNote).all()
    fups = db.query(FollowUpTask).all()
    summaries = db.query(GeneratedSummary).all()
    # patients requiring review: those with open alerts or incomplete docs or overdue followups
    open_alerts = [a for a in alerts if a.status == "open"]
    review_patients = set(a.patient_id for a in open_alerts)
    for n in notes:
        if n.status == "draft":
            review_patients.add(n.patient_id)
    for f in fups:
        if f.status == "pending" and f.due_date < date.today():
            review_patients.add(f.patient_id)
    # overdue investigations count
    overdue = len([a for a in open_alerts if "overdue" in a.title.lower() or "overdue" in a.reason.lower()])
    pending_approvals = len([n for n in notes if n.status == "draft"])
    upcoming = len([f for f in fups if f.status == "pending" and f.due_date >= date.today()])
    # alert distribution
    dist = {}
    for a in open_alerts:
        dist[a.severity] = dist.get(a.severity, 0) + 1
    # recent activity
    recent_patients = [{"id": p.id, "name": p.name} for p in patients[:5]]
    recent_summaries = [{"id": s.id, "patient_id": s.patient_id, "created_at": str(s.created_at)} for s in summaries[-5:]]
    recent_notes = [{"id": n.id, "patient_id": n.patient_id, "status": n.status} for n in notes[-5:]]
    recent_alerts = [{"id": a.id, "patient_id": a.patient_id, "severity": a.severity, "title": a.title} for a in alerts[-5:]]
    # lab overview: count by test
    labs = db.query(LabResult).all()
    lab_counts = {}
    for l in labs:
        lab_counts[l.test_name] = lab_counts.get(l.test_name, 0) + 1
    return {
        "total_patients": len(patients),
        "patients_requiring_review": len(review_patients),
        "outstanding_alerts": len(open_alerts),
        "overdue_investigations": overdue,
        "pending_approvals": pending_approvals,
        "upcoming_followups": upcoming,
        "alert_distribution": dist,
        "lab_overview": lab_counts,
        "recent_patients": recent_patients,
        "recent_summaries": recent_summaries,
        "recent_notes": recent_notes,
        "recent_alerts": recent_alerts,
        "review_queue": list(review_patients),
    }
