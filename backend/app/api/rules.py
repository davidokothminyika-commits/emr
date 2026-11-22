from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ClinicalRule
from .auth import get_current_user
from ..services.rules_engine import sync_rules

router = APIRouter(prefix="/api/rules", tags=["rules"])

@router.get("")
def list_rules(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [{"id": r.id, "rule_id": r.rule_id, "description": r.description, "enabled": r.enabled, "config": r.config} for r in db.query(ClinicalRule).all()]

@router.patch("/{rid}")
def update_rule(rid: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    r = db.query(ClinicalRule).filter(ClinicalRule.rule_id == rid).first()
    if not r: raise HTTPException(404)
    if "enabled" in payload: r.enabled = payload["enabled"]
    db.commit()
    return {"id": r.id, "rule_id": r.rule_id, "description": r.description, "enabled": r.enabled, "config": r.config}
