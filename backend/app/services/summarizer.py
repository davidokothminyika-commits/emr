import json
from datetime import date
from sqlalchemy.orm import Session
from ..models import Patient, Diagnosis, Medication, Allergy, LabResult, Encounter
from ..config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
import httpx

VALID_CATEGORIES = {"patient_overview","active_problems","medication_history","allergies","laboratory_history","clinical_events","outstanding_items"}

def normalize_record(db: Session, patient_id: str) -> dict:
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    dx = db.query(Diagnosis).filter(Diagnosis.patient_id == patient_id).all()
    meds = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    allg = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    labs = db.query(LabResult).filter(LabResult.patient_id == patient_id).all()
    encs = db.query(Encounter).filter(Encounter.patient_id == patient_id).all()
    return {
        "patient": {"id": p.id, "name": p.name, "dob": str(p.dob), "sex": p.sex, "program": p.program, "status": p.status, "facility_id": p.facility_id},
        "diagnoses": [{"id": d.id, "code": d.code, "name": d.name, "date": str(d.date), "status": d.status, "encounter_ref": d.encounter_ref} for d in dx],
        "medications": [{"id": m.id, "name": m.name, "dosage": m.dosage, "frequency": m.frequency, "start_date": str(m.start_date), "end_date": str(m.end_date) if m.end_date else None, "status": m.status} for m in meds],
        "allergies": [{"id": a.id, "allergen": a.allergen, "reaction": a.reaction, "severity": a.severity, "date": str(a.date)} for a in allg],
        "labs": [{"id": l.id, "test_name": l.test_name, "value": l.value, "unit": l.unit, "date": str(l.date), "reference_range": l.reference_range} for l in labs],
        "encounters": [{"id": e.id, "date": str(e.date), "type": e.type, "notes": e.notes, "clinician": e.clinician, "complete": e.complete} for e in encs],
    }

def valid_source_ids(record: dict) -> set:
    ids = set()
    for d in record["diagnoses"]: ids.add(d["id"])
    for m in record["medications"]: ids.add(m["id"])
    for a in record["allergies"]: ids.add(a["id"])
    for l in record["labs"]: ids.add(l["id"])
    for e in record["encounters"]: ids.add(e["id"])
    return ids

def deterministic_summary(record: dict) -> dict:
    pid = record["patient"]["id"]
    statements = []
    # patient overview
    statements.append({"category": "patient_overview", "statement": f"Patient {record['patient']['name']} ({pid}), {record['patient']['sex']}, program: {record['patient']['program']}, status: {record['patient']['status']}.", "source_ids": [], "confidence": "high"})
    # diagnoses
    for d in record["diagnoses"]:
        statements.append({"category": "active_problems", "statement": f"Diagnosis: {d['name']} ({d['code']}) documented {d['date']} (status: {d['status']}).", "source_ids": [d["id"]], "confidence": "high"})
    # meds
    for m in record["medications"]:
        end = m["end_date"] or "ongoing"
        statements.append({"category": "medication_history", "statement": f"Medication: {m['name']} {m['dosage'] or ''} {m['frequency'] or ''}, started {m['start_date']}, ended {end} (status: {m['status']}).", "source_ids": [m["id"]], "confidence": "high"})
    # allergies
    for a in record["allergies"]:
        statements.append({"category": "allergies", "statement": f"Allergy: {a['allergen']} (reaction: {a['reaction'] or 'not specified'}, severity: {a['severity'] or 'not specified'}).", "source_ids": [a["id"]], "confidence": "high"})
    # labs
    for l in record["labs"]:
        statements.append({"category": "laboratory_history", "statement": f"Lab: {l['test_name']} = {l['value']} {l['unit'] or ''} on {l['date']} (ref: {l['reference_range'] or 'n/a'}).", "source_ids": [l["id"]], "confidence": "high"})
    # encounters
    for e in record["encounters"]:
        statements.append({"category": "clinical_events", "statement": f"Encounter {e['type']} on {e['date']} by {e['clinician'] or 'unknown'} (complete: {e['complete']}).", "source_ids": [e["id"]], "confidence": "high"})
    # outstanding items: missing labs? just note count
    statements.append({"category": "outstanding_items", "statement": f"Record contains {len(record['diagnoses'])} diagnoses, {len(record['medications'])} medications, {len(record['allergies'])} allergies, {len(record['labs'])} lab results, {len(record['encounters'])} encounters.", "source_ids": [], "confidence": "medium"})
    return {
        "patient_id": pid,
        "summary": statements,
        "uncertainties": ["Deterministic template summary; no AI interpretation applied."],
        "items_for_clinician_review": [],
    }

def validate_summary(summary: dict, record: dict) -> tuple[bool, list]:
    ids = valid_source_ids(record)
    errors = []
    for s in summary.get("summary", []):
        for sid in s.get("source_ids", []):
            if sid and sid not in ids:
                errors.append(f"Invalid source ID: {sid}")
    return len(errors) == 0, errors

def generate_summary_llm(record: dict) -> dict:
    if not LLM_API_KEY:
        return deterministic_summary(record)
    prompt = f"""You are a clinical documentation assistant. Produce a structured longitudinal clinical summary using ONLY the provided normalized records. Every statement must reference source IDs from the record. Do not invent facts. Return JSON only.

Record:
{json.dumps(record, indent=2)}

Expected JSON:
{{"patient_id": "...", "summary": [{{"category": "...", "statement": "...", "source_ids": ["ID"], "confidence": "high|medium|low"}}], "uncertainties": [], "items_for_clinician_review": []}}

Categories: patient_overview, active_problems, medication_history, allergies, laboratory_history, clinical_events, outstanding_items.
"""
    try:
        with httpx.Client(timeout=60.0) as c:
            r = c.post(f"{LLM_BASE_URL}/chat/completions", headers={"Authorization": f"Bearer {LLM_API_KEY}"}, json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            })
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            summary = json.loads(content)
            ok, errors = validate_summary(summary, record)
            if not ok:
                summary["items_for_clinician_review"] = summary.get("items_for_clinician_review", []) + errors
                # fallback to deterministic if invalid citations dominate
            return summary
    except Exception as e:
        s = deterministic_summary(record)
        s["uncertainties"].append(f"LLM unavailable: {e}")
        return s
