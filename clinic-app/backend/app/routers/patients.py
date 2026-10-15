import unicodedata
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.db import get_session
from app.models import (
    Patient,
    PatientCreate,
    PatientDetail,
    PatientListItem,
    PatientRead,
    PatientUpdate,
    Visit,
)
from app.queries import load_visit_read

router = APIRouter(prefix="/patients", tags=["patients"])


def _norm(text: str) -> str:
    # SQLite lower()/LIKE ignore case only for ASCII, so match in Python.
    return unicodedata.normalize("NFC", text).casefold()


@router.get("", response_model=list[PatientListItem])
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
    last: dict[int, date] = {}
    rows = session.exec(
        select(Visit.patient_id, Visit.visited_at).where(col(Visit.deleted_at).is_(None))
    ).all()
    for patient_id, visited_at in rows:
        if patient_id not in last or visited_at.date() > last[patient_id]:
            last[patient_id] = visited_at.date()
    return [
        PatientListItem(**p.model_dump(), last_visit_date=last.get(p.id))
        for p in patients
    ]


@router.post("", response_model=PatientRead, status_code=201)
def create_patient(data: PatientCreate, session: Session = Depends(get_session)):
    patient = Patient.model_validate(data)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientDetail)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    visits = session.exec(
        select(Visit)
        .where(Visit.patient_id == patient_id, col(Visit.deleted_at).is_(None))
        .order_by(col(Visit.visited_at).desc())
    ).all()
    return PatientDetail(
        **patient.model_dump(), visits=[load_visit_read(session, v) for v in visits]
    )


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
