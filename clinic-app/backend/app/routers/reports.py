from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select

from app import clock
from app.db import get_session
from app.models import (
    DueFollowUpItem,
    DueFollowUpsRead,
    FollowUpRead,
    Patient,
    RevenueRead,
    Visit,
)

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
            col(Visit.deleted_at).is_(None),
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


@router.get("/reports/follow-ups", response_model=DueFollowUpsRead)
def due_follow_ups(
    as_of: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    session: Session = Depends(get_session),
):
    try:
        today = date.fromisoformat(as_of) if as_of is not None else clock.today()
    except ValueError:
        raise HTTPException(status_code=422, detail="as_of must be a valid YYYY-MM-DD date")
    rows = session.exec(
        select(Visit, Patient)
        .join(Patient, Patient.id == Visit.patient_id)
        .where(
            col(Visit.follow_up_date).is_not(None),
            Visit.follow_up_date >= today - timedelta(days=30),
            Visit.follow_up_date <= today,
            col(Visit.deleted_at).is_(None),
            col(Patient.is_archived).is_(False),
        )
    ).all()
    live = session.exec(
        select(Visit.patient_id, Visit.id, Visit.visited_at).where(
            col(Visit.deleted_at).is_(None)
        )
    ).all()
    visits: dict[int, list[tuple[int, datetime]]] = {}
    for patient_id, visit_id, visited_at in live:
        visits.setdefault(patient_id, []).append((visit_id, visited_at))
    best: dict[int, tuple[Visit, Patient]] = {}
    for v, p in rows:
        start = datetime.combine(v.follow_up_date, time.min)
        if any(vid != v.id and at >= start for vid, at in visits.get(p.id, [])):
            continue
        if p.id not in best or v.follow_up_date > best[p.id][0].follow_up_date:
            best[p.id] = (v, p)
    items = [
        DueFollowUpItem(
            patient_id=p.id,
            full_name=p.full_name,
            phone=p.phone,
            follow_up_date=v.follow_up_date,
            days_overdue=(today - v.follow_up_date).days,
        )
        for v, p in best.values()
    ]
    items.sort(key=lambda i: (-i.days_overdue, i.full_name, i.patient_id))
    return DueFollowUpsRead(total=len(items), items=items)


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
            Visit.visited_at < end,
            col(Visit.deleted_at).is_(None),
        )
    ).all()
    return RevenueRead(
        visit_count=len(visits),
        collected=sum(v.paid_amount for v in visits),
        owed=sum(v.fee - v.paid_amount for v in visits),
    )
