from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ClinicalAlert
from ..schemas import AlertOut
from .auth import get_current_user
from .intelligence import alert_out
from ..services.audit import log_action

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("")
def list_alerts(severity: str = None, patient_id: str = None, rule_id: str = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(ClinicalAlert)
    if severity: q = q.filter(ClinicalAlert.severity == severity)
    if patient_id: q = q.filter(ClinicalAlert.patient_id == patient_id)
    if rule_id: q = q.filter(ClinicalAlert.rule_id == rule_id)
    return [alert_out(a) for a in q.all()]

@router.patch("/{aid}/review")
def review_alert(aid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    a = db.query(ClinicalAlert).filter(ClinicalAlert.id == aid).first()
    if not a: raise HTTPException(404)
    a.status = "reviewed"
    a.reviewed_by = user.id
    from datetime import datetime
    a.reviewed_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "alert_review", "alert", aid)
    return alert_out(a)

@router.patch("/{aid}/dismiss")
def dismiss_alert(aid: str, reason: str = "", db: Session = Depends(get_db), user=Depends(get_current_user)):
    a = db.query(ClinicalAlert).filter(ClinicalAlert.id == aid).first()
    if not a: raise HTTPException(404)
    a.status = "dismissed"
    a.dismissed_reason = reason
    a.reviewed_by = user.id
    from datetime import datetime
    a.reviewed_at = datetime.utcnow()
    db.commit()
    log_action(db, user.id, "alert_dismiss", "alert", aid, {"reason": reason})
    return alert_out(a)

@router.patch("/{aid}/reopen")
def reopen_alert(aid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    a = db.query(ClinicalAlert).filter(ClinicalAlert.id == aid).first()
    if not a: raise HTTPException(404)
    a.status = "open"
    db.commit()
    log_action(db, user.id, "alert_reopen", "alert", aid)
    return alert_out(a)
