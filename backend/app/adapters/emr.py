import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy.orm import Session
from ..models import Patient, Diagnosis, Medication, Allergy, LabResult, Encounter
from ..config import OPENMRS_BASE_URL, OPENMRS_USERNAME, OPENMRS_PASSWORD, EMR_MODE


class NormalizedPatientRecord:
    def __init__(self, patient, diagnoses, medications, allergies, labs, encounters):
        self.patient = patient
        self.diagnoses = diagnoses
        self.medications = medications
        self.allergies = allergies
        self.labs = labs
        self.encounters = encounters

    def to_dict(self):
        return {
            "patient": patient_to_dict(self.patient),
            "diagnoses": [d.__dict__ for d in self.diagnoses],
            "medications": [m.__dict__ for m in self.medications],
            "allergies": [a.__dict__ for a in self.allergies],
            "labs": [l.__dict__ for l in self.labs],
            "encounters": [e.__dict__ for e in self.encounters],
        }


def patient_to_dict(p):
    return {
        "id": p.id, "name": p.name, "dob": str(p.dob), "sex": p.sex,
        "facility_id": p.facility_id, "registration_date": str(p.registration_date),
        "program": p.program, "status": p.status,
    }


class EMRAdapter:
    def get_patients(self, db: Session) -> List[Patient]: raise NotImplementedError
    def get_patient(self, db: Session, pid: str) -> Optional[Patient]: raise NotImplementedError
    def get_record(self, db: Session, pid: str) -> NormalizedPatientRecord: raise NotImplementedError


class SyntheticEMRAdapter(EMRAdapter):
    def get_patients(self, db):
        return db.query(Patient).all()
    def get_patient(self, db, pid):
        return db.query(Patient).filter(Patient.id == pid).first()
    def get_record(self, db, pid):
        p = self.get_patient(db, pid)
        if not p:
            return None
        return NormalizedPatientRecord(
            p,
            db.query(Diagnosis).filter(Diagnosis.patient_id == pid).all(),
            db.query(Medication).filter(Medication.patient_id == pid).all(),
            db.query(Allergy).filter(Allergy.patient_id == pid).all(),
            db.query(LabResult).filter(LabResult.patient_id == pid).all(),
            db.query(Encounter).filter(Encounter.patient_id == pid).all(),
        )


class OpenMRSAdapter(EMRAdapter):
    """Connector skeleton for OpenMRS/KenyaEMR. Not active by default."""
    def __init__(self):
        self.base_url = OPENMRS_BASE_URL.rstrip("/")
        self.username = OPENMRS_USERNAME
        self.password = OPENMRS_PASSWORD

    def _client(self):
        return httpx.Client(base_url=self.base_url, auth=(self.username, self.password), timeout=30.0, verify=False)

    def get_patients(self, db):
        # Would call /ws/rest/v1/patient; mapping not implemented without live server
        raise NotImplementedError("OpenMRS live connection not configured. Use synthetic mode.")

    def get_patient(self, db, pid):
        raise NotImplementedError("OpenMRS live connection not configured. Use synthetic mode.")

    def get_record(self, db, pid):
        raise NotImplementedError("OpenMRS live connection not configured. Use synthetic mode.")


def get_adapter():
    if EMR_MODE == "openmrs" and OPENMRS_BASE_URL:
        return OpenMRSAdapter()
    return SyntheticEMRAdapter()
