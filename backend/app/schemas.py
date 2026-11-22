from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List, Any, Dict

class LoginRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    full_name: str
    role: str

class PatientOut(BaseModel):
    id: str
    name: str
    dob: date
    sex: str
    facility_id: str
    registration_date: date
    program: str
    status: str

class DiagnosisOut(BaseModel):
    id: str
    patient_id: str
    code: str
    name: str
    date: date
    status: str
    encounter_ref: Optional[str]
    origin: str

class MedicationOut(BaseModel):
    id: str
    patient_id: str
    name: str
    dosage: Optional[str]
    frequency: Optional[str]
    start_date: date
    end_date: Optional[date]
    status: str
    encounter_ref: Optional[str]
    origin: str

class AllergyOut(BaseModel):
    id: str
    patient_id: str
    allergen: str
    reaction: Optional[str]
    severity: Optional[str]
    date: date
    encounter_ref: Optional[str]
    origin: str

class LabResultOut(BaseModel):
    id: str
    patient_id: str
    test_name: str
    value: str
    unit: Optional[str]
    date: date
    reference_range: Optional[str]
    encounter_ref: Optional[str]
    origin: str

class EncounterOut(BaseModel):
    id: str
    patient_id: str
    date: date
    type: str
    notes: Optional[str]
    clinician: Optional[str]
    complete: bool
    origin: str

class PatientHistory(BaseModel):
    patient: PatientOut
    diagnoses: List[DiagnosisOut]
    medications: List[MedicationOut]
    allergies: List[AllergyOut]
    labs: List[LabResultOut]
    encounters: List[EncounterOut]

class AlertOut(BaseModel):
    id: str
    patient_id: str
    rule_id: str
    title: str
    severity: str
    reason: str
    trigger_date: date
    source_ids: List[str]
    evidence_dates: List[str]
    recommended_action: Optional[str]
    status: str
    dismissed_reason: Optional[str]

class FollowUpOut(BaseModel):
    id: str
    patient_id: str
    description: str
    due_date: date
    priority: str
    related_record_id: Optional[str]
    status: str
    assigned_clinician: Optional[str]

class RuleOut(BaseModel):
    id: str
    rule_id: str
    description: str
    enabled: bool
    config: Dict[str, Any]

class AuditOut(BaseModel):
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    timestamp: datetime
    details: Optional[Dict[str, Any]]

class SummaryStatement(BaseModel):
    category: str
    statement: str
    source_ids: List[str]
    confidence: str

class SummaryOut(BaseModel):
    id: str
    patient_id: str
    content: Dict[str, Any]
    status: str
    version: int
    created_at: datetime

class NoteOut(BaseModel):
    id: str
    patient_id: str
    content: Dict[str, Any]
    status: str
    created_at: datetime

class ReferralOut(BaseModel):
    id: str
    patient_id: str
    content: Dict[str, Any]
    status: str
    created_at: datetime
