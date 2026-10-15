from sqlmodel import Session, select

from app.models import PrescriptionItem, PrescriptionItemRead, Visit, VisitRead


def load_visit_read(session: Session, visit: Visit) -> VisitRead:
    items = session.exec(
        select(PrescriptionItem)
        .where(PrescriptionItem.visit_id == visit.id)
        .order_by(PrescriptionItem.id)
    ).all()
    return VisitRead(
        **visit.model_dump(),
        items=[PrescriptionItemRead.model_validate(i) for i in items],
    )
