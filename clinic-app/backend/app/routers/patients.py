import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Patient, PatientCreate, PatientRead, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


def _norm(text: str) -> str:
    # SQLite lower()/LIKE ignore case only for ASCII, so match in Python.
    return unicodedata.normalize("NFC", text).casefold()


@router.get("", response_model=list[PatientRead])
def list_patients(
    q: str | None = None,
    include_archived: bool = False,
    session: Session = Depends(get_session),
):
    patients = session.exec(select(Patient).order_by(Patient.full_name)).all()
    if not include_archived:
        patients = [p for p in patients if not p.is_archived]
    if q and q.strip():
        needle = _norm(q.strip())
        patients = [
            p
            for p in patients
            if needle in _norm(p.full_name) or needle in (p.phone or "")
        ]
    return patients


@router.post("", response_model=PatientRead, status_code=201)
def create_patient(data: PatientCreate, session: Session = Depends(get_session)):
    patient = Patient.model_validate(data)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientRead)
def update_patient(
    patient_id: int, data: PatientUpdate, session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient
