from datetime import date, datetime
from .database import SessionLocal
from .models import User, Patient, Diagnosis, Medication, Allergy, LabResult, Encounter, FollowUpTask, ClinicalRule
from .services.auth import hash_pw

def seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(Patient).count() > 0:
            return
        # users
        db.add(User(id="U-CLIN", username="clinician", full_name="Dr. Amina Odhiambo", role="clinician", password_hash=hash_pw("demo123")))
        db.add(User(id="U-ADMIN", username="admin", full_name="System Administrator", role="administrator", password_hash=hash_pw("admin123")))
        db.commit()

        patients = [
            ("P-0001","James Otieno", date(1985,3,12),"Male","FAC-001",date(2019,1,10),"HIV care","active"),
            ("P-0002","Mary Wanjiku", date(1990,7,22),"Female","FAC-001",date(2020,2,5),"HIV care","active"),
            ("P-0003","Peter Mwangi", date(1972,11,3),"Male","FAC-002",date(2018,6,15),"Type 2 Diabetes","active"),
            ("P-0004","Grace Achieng", date(1988,9,18),"Female","FAC-001",date(2021,3,20),"HIV care","active"),
            ("P-0005","David Kiptoo", date(1979,1,25),"Male","FAC-002",date(2019,8,1),"HIV care","active"),
            ("P-0006","Sarah Njeri", date(1995,4,9),"Female","FAC-001",date(2022,1,12),"General care","active"),
            ("P-0007","John Kamau", date(1982,6,30),"Male","FAC-002",date(2020,9,5),"HIV care","active"),
            ("P-0008","Esther Chebet", date(1993,12,14),"Female","FAC-001",date(2021,7,8),"HIV care","active"),
        ]
        for pid,name,dob,sex,fac,reg,prog,status in patients:
            db.add(Patient(id=pid,name=name,dob=dob,sex=sex,facility_id=fac,registration_date=reg,program=prog,status=status))
        db.commit()

        # Diagnoses
        dxs = [
            ("D-0001","P-0001","B20","HIV infection",date(2019,1,10),"active","E-0001"),
            ("D-0002","P-0002","B20","HIV infection",date(2020,2,5),"active","E-0002"),
            ("D-0003","P-0003","E11","Type 2 Diabetes Mellitus",date(2018,6,15),"active","E-0003"),
            ("D-0004","P-0004","B20","HIV infection",date(2021,3,20),"active","E-0004"),
            ("D-0005","P-0004","Z88.0","Allergy to penicillin (documented)",date(2021,3,20),"active","E-0004"),
            ("D-0006","P-0005","B20","HIV infection",date(2019,8,1),"active","E-0005"),
            ("D-0007","P-0006","J06.9","Acute upper respiratory infection",date(2022,1,12),"resolved","E-0006"),
            ("D-0008","P-0007","B20","HIV infection",date(2020,9,5),"active","E-0007"),
            ("D-0009","P-0008","B20","HIV infection",date(2021,7,8),"active","E-0008"),
            ("D-0010","P-0007","CONF","Conflicting CD4 documentation",date(2021,1,1),"active","E-0007"),
        ]
        for d in dxs:
            db.add(Diagnosis(id=d[0],patient_id=d[1],code=d[2],name=d[3],date=d[4],status=d[5],encounter_ref=d[6]))
        db.commit()

        # Medications
        meds = [
            ("M-0001","P-0001","TDF/3TC/DTG","300/300/50mg","once daily",date(2019,1,10),None,"active","E-0001"),
            ("M-0002","P-0002","TDF/3TC/EFV","300/300/600mg","once daily",date(2020,2,5),date(2021,6,1),"ended","E-0002"),
            ("M-0003","P-0002","TDF/3TC/DTG","300/300/50mg","once daily",date(2021,6,2),None,"active","E-0002b"),
            ("M-0004","P-0003","Metformin","500mg","twice daily",date(2018,6,15),None,"active","E-0003"),
            ("M-0005","P-0004","Amoxicillin","500mg","three times daily",date(2021,4,1),date(2021,4,7),"ended","E-0004"),
            ("M-0006","P-0005","AZT/3TC/NVP","300/150/200mg","twice daily",date(2019,8,1),date(2020,10,1),"ended","E-0005"),
            ("M-0007","P-0005","TDF/3TC/DTG","300/300/50mg","once daily",date(2020,10,2),None,"active","E-0005b"),
            ("M-0008","P-0008","TDF/3TC/DTG","300/300/50mg","once daily",date(2021,7,8),None,"active","E-0008"),
        ]
        for m in meds:
            db.add(Medication(id=m[0],patient_id=m[1],name=m[2],dosage=m[3],frequency=m[4],start_date=m[5],end_date=m[6],status=m[7],encounter_ref=m[8]))
        db.commit()

        # Allergies
        allg = [
            ("A-0001","P-0004","Penicillin","Rash","moderate",date(2021,3,20),"E-0004"),
            ("A-0002","P-0006","Sulfonamides","Unknown","mild",date(2022,1,12),"E-0006"),
        ]
        for a in allg:
            db.add(Allergy(id=a[0],patient_id=a[1],allergen=a[2],reaction=a[3],severity=a[4],date=a[5],encounter_ref=a[6]))
        db.commit()

        # Labs
        labs = [
            ("L-0001","P-0001","HIV Viral Load","45","copies/mL",date(2023,1,15),"0-50","E-L1"),
            ("L-0002","P-0001","HIV Viral Load","<50","copies/mL",date(2023,7,20),"0-50","E-L2"),
            ("L-0003","P-0001","CD4 Count","620","cells/uL",date(2023,7,20),"500-1500","E-L2"),
            ("L-0004","P-0002","HIV Viral Load","1200","copies/mL",date(2022,3,10),"0-50","E-L3"),
            ("L-0005","P-0002","HIV Viral Load","<50","copies/mL",date(2022,9,5),"0-50","E-L4"),
            ("L-0006","P-0002","CD4 Count","480","cells/uL",date(2022,9,5),"500-1500","E-L4"),
            ("L-0007","P-0003","HbA1c","7.2","%",date(2023,2,10),"<7.0","E-L5"),
            ("L-0008","P-0003","HbA1c","7.8","%",date(2023,8,15),"<7.0","E-L6"),
            ("L-0009","P-0003","Creatinine","1.1","mg/dL",date(2023,8,15),"0.7-1.3","E-L6"),
            ("L-0010","P-0004","HIV Viral Load","<50","copies/mL",date(2023,5,1),"0-50","E-L7"),
            ("L-0011","P-0005","HIV Viral Load","350","copies/mL",date(2023,4,1),"0-50","E-L8"),
            ("L-0012","P-0007","HIV Viral Load","<50","copies/mL",date(2023,6,1),"0-50","E-L9"),
            ("L-0013","P-0007","CD4 Count","300","cells/uL",date(2023,6,1),"500-1500","E-L9"),
            ("L-0014","P-0008","HIV Viral Load","<50","copies/mL",date(2023,9,1),"0-50","E-L10"),
            ("L-0015","P-0008","Full Blood Count","Normal","x10^9/L",date(2023,9,1),"N/A","E-L10"),
        ]
        for l in labs:
            db.add(LabResult(id=l[0],patient_id=l[1],test_name=l[2],value=l[3],unit=l[4],date=l[5],reference_range=l[6],encounter_ref=l[7]))
        db.commit()

        # Encounters
        encs = [
            ("E-0001","P-0001",date(2019,1,10),"Enrollment","HIV care enrollment", "Dr. Amina", True),
            ("E-0002","P-0002",date(2020,2,5),"Enrollment","HIV care enrollment", "Dr. Amina", True),
            ("E-0002b","P-0002",date(2021,6,2),"Follow-up","Regimen switch to DTG", "Dr. Amina", True),
            ("E-0003","P-0003",date(2018,6,15),"Diagnosis","Type 2 diabetes diagnosed", "Dr. Otieno", True),
            ("E-0004","P-0004",date(2021,3,20),"Enrollment","HIV care enrollment; allergy documented", "Dr. Amina", True),
            ("E-0005","P-0005",date(2019,8,1),"Enrollment","HIV care enrollment", "Dr. Amina", True),
            ("E-0005b","P-0005",date(2020,10,2),"Follow-up","Regimen switch", "Dr. Amina", True),
            ("E-0006","P-0006",date(2022,1,12),"Consultation","URTI treated", "Dr. Otieno", True),
            ("E-0007","P-0007",date(2020,9,5),"Enrollment","HIV care enrollment", "Dr. Amina", True),
            ("E-0008","P-0008",date(2021,7,8),"Enrollment","HIV care enrollment", "Dr. Amina", True),
            ("E-0009","P-0005",date(2023,9,1),"Follow-up","Latest encounter incomplete", "Dr. Amina", False),
        ]
        for e in encs:
            db.add(Encounter(id=e[0],patient_id=e[1],date=e[2],type=e[3],notes=e[4],clinician=e[5],complete=e[6]))
        db.commit()

        # Follow-ups
        fups = [
            ("FU-0001","P-0006","Pending follow-up visit","Pending follow-up visit", date(2023,1,1),"high", None, "pending", "Dr. Otieno"),
            ("FU-0002","P-0003","HbA1c follow-up","HbA1c follow-up", date(2023,6,1),"medium", "L-0008", "pending", "Dr. Otieno"),
        ]
        for f in fups:
            db.add(FollowUpTask(id=f[0],patient_id=f[1],title=f[2],description=f[3],due_date=f[4],priority=f[5],related_record_id=f[6],status=f[7],assigned_clinician=f[8],created_by="U-CLIN"))
        db.commit()
    finally:
        db.close()
