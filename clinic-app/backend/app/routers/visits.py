from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app import clock
from app.db import get_session
from app.models import Patient, PrescriptionItem, Visit, VisitRead, VisitWrite
from app.queries import load_visit_read

router = APIRouter(tags=["visits"])


def _get_patient(session: Session, patient_id: int) -> Patient:
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def _require_active(patient: Patient) -> None:
    if patient.is_archived:
        raise HTTPException(status_code=409, detail="Patient is archived")


def _get_visit(session: Session, visit_id: int, include_deleted: bool = False) -> Visit:
    visit = session.get(Visit, visit_id)
    if not visit or (visit.deleted_at is not None and not include_deleted):
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@router.post("/patients/{patient_id}/visits", response_model=VisitRead, status_code=201)
def create_visit(patient_id: int, data: VisitWrite, session: Session = Depends(get_session)):
    _require_active(_get_patient(session, patient_id))
    visit = Visit(**data.model_dump(exclude={"items"}), patient_id=patient_id)
    session.add(visit)
    session.flush()
    for item in data.items:
        session.add(PrescriptionItem(**item.model_dump(), visit_id=visit.id))
    session.commit()
    session.refresh(visit)
    return load_visit_read(session, visit)


@router.get("/visits/{visit_id}", response_model=VisitRead)
def get_visit(visit_id: int, session: Session = Depends(get_session)):
    return load_visit_read(session, _get_visit(session, visit_id))


@router.put("/visits/{visit_id}", response_model=VisitRead)
def update_visit(visit_id: int, data: VisitWrite, session: Session = Depends(get_session)):
    visit = _get_visit(session, visit_id)
    _require_active(_get_patient(session, visit.patient_id))
    visit.sqlmodel_update(data.model_dump(exclude={"items"}))
    old_items = session.exec(
        select(PrescriptionItem).where(PrescriptionItem.visit_id == visit.id)
    ).all()
    for old in old_items:
        session.delete(old)
    for item in data.items:
        session.add(PrescriptionItem(**item.model_dump(), visit_id=visit.id))
    session.add(visit)
    session.commit()
    session.refresh(visit)
    return load_visit_read(session, visit)


@router.delete("/visits/{visit_id}")
def delete_visit(visit_id: int, session: Session = Depends(get_session)):
    visit = _get_visit(session, visit_id)
    visit.deleted_at = clock.now()
    session.add(visit)
    session.commit()
    return {"ok": True}


@router.post("/visits/{visit_id}/restore", response_model=VisitRead)
def restore_visit(visit_id: int, session: Session = Depends(get_session)):
    visit = _get_visit(session, visit_id, include_deleted=True)
    if visit.deleted_at is None:
        raise HTTPException(status_code=409, detail="Visit is not deleted")
    _require_active(_get_patient(session, visit.patient_id))
    visit.deleted_at = None
    session.add(visit)
    session.commit()
    session.refresh(visit)
    return load_visit_read(session, visit)
