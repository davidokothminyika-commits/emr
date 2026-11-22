import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, DateTime, Date, Float, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def uid(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uid("U-"))
    username: Mapped[str] = mapped_column(String, unique=True)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)  # clinician | administrator
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    dob: Mapped[date] = mapped_column(Date)
    sex: Mapped[str] = mapped_column(String)
    facility_id: Mapped[str] = mapped_column(String)
    registration_date: Mapped[date] = mapped_column(Date)
    program: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    diagnoses: Mapped[list["Diagnosis"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    medications: Mapped[list["Medication"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    allergies: Mapped[list["Allergy"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    labs: Mapped[list["LabResult"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    encounters: Mapped[list["Encounter"]] = relationship(back_populates="patient", cascade="all, delete-orphan")

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String, default="active")
    encounter_ref: Mapped[str] = mapped_column(String, nullable=True)
    origin: Mapped[str] = mapped_column(String, default="synthetic_emr")
    patient = relationship("Patient", back_populates="diagnoses")

class Medication(Base):
    __tablename__ = "medications"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    name: Mapped[str] = mapped_column(String)
    dosage: Mapped[str] = mapped_column(String, nullable=True)
    frequency: Mapped[str] = mapped_column(String, nullable=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")
    encounter_ref: Mapped[str] = mapped_column(String, nullable=True)
    origin: Mapped[str] = mapped_column(String, default="synthetic_emr")
    patient = relationship("Patient", back_populates="medications")

class Allergy(Base):
    __tablename__ = "allergies"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    allergen: Mapped[str] = mapped_column(String)
    reaction: Mapped[str] = mapped_column(String, nullable=True)
    severity: Mapped[str] = mapped_column(String, nullable=True)
    date: Mapped[date] = mapped_column(Date)
    encounter_ref: Mapped[str] = mapped_column(String, nullable=True)
    origin: Mapped[str] = mapped_column(String, default="synthetic_emr")
    patient = relationship("Patient", back_populates="allergies")

class LabResult(Base):
    __tablename__ = "lab_results"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    test_name: Mapped[str] = mapped_column(String)
    value: Mapped[str] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String, nullable=True)
    date: Mapped[date] = mapped_column(Date)
    reference_range: Mapped[str] = mapped_column(String, nullable=True)
    encounter_ref: Mapped[str] = mapped_column(String, nullable=True)
    origin: Mapped[str] = mapped_column(String, default="synthetic_emr")
    patient = relationship("Patient", back_populates="labs")

class Encounter(Base):
    __tablename__ = "encounters"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    clinician: Mapped[str] = mapped_column(String, nullable=True)
    complete: Mapped[bool] = mapped_column(Boolean, default=True)
    origin: Mapped[str] = mapped_column(String, default="synthetic_emr")
    patient = relationship("Patient", back_populates="encounters")

class ClinicalRule(Base):
    __tablename__ = "clinical_rules"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    rule_id: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

class ClinicalAlert(Base):
    __tablename__ = "clinical_alerts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    rule_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text)
    trigger_date: Mapped[date] = mapped_column(Date)
    source_ids: Mapped[list] = mapped_column(JSON, default=list)
    evidence_dates: Mapped[list] = mapped_column(JSON, default=list)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="open")  # open | reviewed | dismissed | reopened
    dismissed_reason: Mapped[str] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str] = mapped_column(String, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class GeneratedSummary(Base):
    __tablename__ = "generated_summaries"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    content: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String, default="draft")  # draft | approved | rejected
    reviewer_id: Mapped[str] = mapped_column(String, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    edited_content: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class EncounterNote(Base):
    __tablename__ = "encounter_notes"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    content: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="draft")
    reviewer_id: Mapped[str] = mapped_column(String, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    edited_content: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FollowUpTask(Base):
    __tablename__ = "followup_tasks"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    description: Mapped[str] = mapped_column(Text)
    due_date: Mapped[date] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String, default="medium")
    related_record_id: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    assigned_clinician: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Referral(Base):
    __tablename__ = "referrals"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    content: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    resource_type: Mapped[str] = mapped_column(String)
    resource_id: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
