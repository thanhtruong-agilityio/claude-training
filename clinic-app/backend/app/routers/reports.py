from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select

from app import clock
from app.db import get_session
from app.models import FollowUpRead, Patient, RevenueRead, Visit

router = APIRouter(tags=["reports"])


@router.get("/visits/follow-ups", response_model=list[FollowUpRead])
def follow_ups(
    on: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
):
    day = on or clock.today()
    rows = session.exec(
        select(Visit, Patient)
        .join(Patient, Patient.id == Visit.patient_id)
        .where(
            Visit.follow_up_date == day,
            col(Patient.is_archived).is_(False),
        )
        .order_by(Patient.full_name)
    ).all()
    return [
        FollowUpRead(
            visit_id=v.id,
            patient_id=p.id,
            full_name=p.full_name,
            phone=p.phone,
            follow_up_date=v.follow_up_date,
        )
        for v, p in rows
    ]


@router.get("/reports/revenue", response_model=RevenueRead)
def revenue(
    from_: date = Query(alias="from"),
    to: date = Query(),
    session: Session = Depends(get_session),
):
    if from_ > to:
        raise HTTPException(status_code=422, detail="from must not be after to")
    start = datetime.combine(from_, time.min)
    end = datetime.combine(to + timedelta(days=1), time.min)
    visits = session.exec(
        select(Visit).where(
            Visit.visited_at >= start,
            Visit.visited_at <= end,
            col(Visit.deleted_at).is_(None),
        )
    ).all()
    return RevenueRead(
        visit_count=len(visits),
        collected=sum(v.paid_amount for v in visits),
        owed=sum(v.fee for v in visits),
    )
