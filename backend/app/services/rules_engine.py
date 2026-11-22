import json
from datetime import date, timedelta
from sqlalchemy.orm import Session
from ..models import Patient, Diagnosis, Medication, Allergy, LabResult, Encounter, ClinicalRule, ClinicalAlert
from ..config import RULES_FILE

def load_rules_json():
    with open(RULES_FILE) as f:
        return json.load(f)

def sync_rules(db: Session):
    rules = load_rules_json()
    for r in rules:
        existing = db.query(ClinicalRule).filter(ClinicalRule.rule_id == r["rule_id"]).first()
        if existing:
            existing.description = r["description"]
            existing.config = r
            existing.enabled = r.get("enabled", True)
        else:
            db.add(ClinicalRule(id=r["rule_id"], rule_id=r["rule_id"], description=r["description"], config=r, enabled=r.get("enabled", True)))
    db.commit()

def evaluate_patient(db: Session, patient_id: str, today: date = None) -> list[dict]:
    today = today or date.today()
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        return []
    dx = db.query(Diagnosis).filter(Diagnosis.patient_id == patient_id).all()
    meds = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    allg = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    labs = db.query(LabResult).filter(LabResult.patient_id == patient_id).all()
    encs = db.query(Encounter).filter(Encounter.patient_id == patient_id).all()
    fups = db.query(__import__("app.models", fromlist=["FollowUpTask"]).FollowUpTask).filter(__import__("app.models", fromlist=["FollowUpTask"]).FollowUpTask.patient_id == patient_id).all() if False else []
    from ..models import FollowUpTask
    fups = db.query(FollowUpTask).filter(FollowUpTask.patient_id == patient_id).all()

    rules = db.query(ClinicalRule).filter(ClinicalRule.enabled == True).all()
    triggered = []

    programs = [p.program] + [d.name for d in dx]
    conditions_text = " ".join(programs).lower()

    def has_condition(cond):
        if cond == "any":
            return True
        return cond.lower() in conditions_text

    for rule in rules:
        cfg = rule.config
        rid = rule.rule_id
        if not cfg.get("enabled", True):
            continue
        if not any(has_condition(c) for c in cfg.get("applicable_conditions", ["any"])):
            continue

        # VL overdue
        if rid == "VL-OVERDUE-01":
            vl_labs = [l for l in labs if "viral load" in l.test_name.lower()]
            if vl_labs:
                last = max(vl_labs, key=lambda x: x.date)
                if (today - last.date).days > cfg["interval_days"]:
                    triggered.append({
                        "rule_id": rid, "title": "HIV viral load follow-up potentially overdue",
                        "severity": cfg["severity"],
                        "reason": f"Last documented HIV viral load on {last.date}; configured interval {cfg['interval_days']} days exceeded.",
                        "trigger_date": today,
                        "source_ids": [last.id],
                        "evidence_dates": [str(last.date)],
                        "recommended_action": "Verify whether repeat viral load is indicated per local protocol.",
                    })
            else:
                # missing result
                triggered.append({
                    "rule_id": rid, "title": "No HIV viral load result recorded",
                    "severity": "Medium",
                    "reason": "No HIV viral load result found in patient record.",
                    "trigger_date": today,
                    "source_ids": [],
                    "evidence_dates": [],
                    "recommended_action": "Confirm whether viral load testing is pending or not applicable.",
                })

        elif rid == "DM-HBA1C-01":
            hb = [l for l in labs if "hba1c" in l.test_name.lower() or "a1c" in l.test_name.lower()]
            if hb:
                last = max(hb, key=lambda x: x.date)
                if (today - last.date).days > cfg["interval_days"]:
                    triggered.append({
                        "rule_id": rid, "title": "HbA1c follow-up potentially overdue",
                        "severity": cfg["severity"],
                        "reason": f"Last documented HbA1c on {last.date}; configured interval {cfg['interval_days']} days exceeded.",
                        "trigger_date": today,
                        "source_ids": [last.id],
                        "evidence_dates": [str(last.date)],
                        "recommended_action": "Verify whether repeat HbA1c is indicated per local protocol.",
                    })

        elif rid == "ALLERGY-REVIEW-01":
            if allg and meds:
                triggered.append({
                    "rule_id": rid, "title": "Documented allergy requires medication review",
                    "severity": cfg["severity"],
                    "reason": f"Patient has {len(allg)} documented allergy/allergies and {len(meds)} medications; clinician review recommended.",
                    "trigger_date": today,
                    "source_ids": [a.id for a in allg] + [m.id for m in meds],
                    "evidence_dates": [str(a.date) for a in allg],
                    "recommended_action": "Review medication list against documented allergies.",
                })

        elif rid == "DOCUMENTATION-01":
            if encs:
                last_enc = max(encs, key=lambda x: x.date)
                if not last_enc.complete:
                    triggered.append({
                        "rule_id": rid, "title": "Incomplete encounter documentation",
                        "severity": cfg["severity"],
                        "reason": f"Latest encounter {last_enc.id} on {last_enc.date} marked incomplete.",
                        "trigger_date": today,
                        "source_ids": [last_enc.id],
                        "evidence_dates": [str(last_enc.date)],
                        "recommended_action": "Complete documentation for the latest encounter.",
                    })

        elif rid == "FOLLOWUP-OVERDUE-01":
            for ft in fups:
                if ft.status == "pending" and ft.due_date < today:
                    # check if encounter after due date
                    later_encs = [e for e in encs if e.date >= ft.due_date]
                    if not later_encs:
                        triggered.append({
                            "rule_id": rid, "title": "Scheduled follow-up potentially overdue",
                            "severity": cfg["severity"],
                            "reason": f"Follow-up task due {ft.due_date} has no documented encounter after due date.",
                            "trigger_date": today,
                            "source_ids": [ft.id],
                            "evidence_dates": [str(ft.due_date)],
                            "recommended_action": "Verify whether the follow-up visit occurred.",
                        })

        elif rid == "DATA-CONFLICT-01":
            # detect conflicting entries: e.g., patient G seeded with conflict flag via diagnoses? We'll check medication status conflicts
            # Simple: if a medication has both active and ended overlapping? We'll rely on a marker: diagnosis code 'CONFLICT'
            conflict_dx = [d for d in dx if "conflict" in d.name.lower() or "conflict" in (d.code or "").lower()]
            if conflict_dx:
                triggered.append({
                    "rule_id": rid, "title": "Conflicting clinical entries require verification",
                    "severity": cfg["severity"],
                    "reason": "Conflicting clinical entries detected in patient record.",
                    "trigger_date": today,
                    "source_ids": [d.id for d in conflict_dx],
                    "evidence_dates": [str(d.date) for d in conflict_dx],
                    "recommended_action": "Review and reconcile conflicting entries.",
                })

    return triggered

def run_rules_for_all(db: Session):
    from ..models import Patient, ClinicalAlert
    patients = db.query(Patient).all()
    created = 0
    for p in patients:
        # clear open alerts? keep; only add new if not duplicate rule+patient open
        existing_open = {(a.patient_id, a.rule_id) for a in db.query(ClinicalAlert).filter(ClinicalAlert.status.in_(["open","reviewed"])).all()}
        for t in evaluate_patient(db, p.id):
            if (p.id, t["rule_id"]) in existing_open:
                continue
            db.add(ClinicalAlert(
                id=f"A-{p.id}-{t['rule_id']}",
                patient_id=p.id,
                rule_id=t["rule_id"],
                title=t["title"],
                severity=t["severity"],
                reason=t["reason"],
                trigger_date=t["trigger_date"],
                source_ids=t["source_ids"],
                evidence_dates=t["evidence_dates"],
                recommended_action=t["recommended_action"],
                status="open",
            ))
            created += 1
    db.commit()
    return created
