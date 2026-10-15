from datetime import date, datetime
from typing import Literal

from pydantic import NaiveDatetime, field_validator, model_validator
from sqlmodel import Field, SQLModel

Sex = Literal["male", "female", "other"]


def _strip(value):
    return value.strip() if isinstance(value, str) else value


class PatientBase(SQLModel):
    full_name: str = Field(min_length=1, max_length=200)
    birth_year: int | None = Field(default=None, ge=1900)
    sex: str | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
    allergies: str | None = None
    medical_history: str | None = None

    _strip_text = field_validator(
        "full_name", "phone", "address", "allergies", "medical_history", mode="before"
    )(_strip)

    @field_validator("birth_year")
    @classmethod
    def _birth_year_not_in_future(cls, value):
        if value is not None and value > date.today().year:
            raise ValueError("birth_year cannot be in the future")
        return value


class Patient(PatientBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_archived: bool = False
    created_at: NaiveDatetime = Field(default_factory=datetime.now)


class PatientCreate(PatientBase):
    sex: Sex | None = None


class PatientUpdate(SQLModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    birth_year: int | None = Field(default=None, ge=1900)
    sex: Sex | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
    allergies: str | None = None
    medical_history: str | None = None
    is_archived: bool | None = None

    _strip_text = field_validator(
        "full_name", "phone", "address", "allergies", "medical_history", mode="before"
    )(_strip)

    @field_validator("full_name", "is_archived")
    @classmethod
    def _not_null(cls, value):
        if value is None:
            raise ValueError("must not be null")
        return value

    @field_validator("birth_year")
    @classmethod
    def _birth_year_not_in_future(cls, value):
        if value is not None and value > date.today().year:
            raise ValueError("birth_year cannot be in the future")
        return value


class PatientRead(PatientBase):
    id: int
    is_archived: bool
    created_at: NaiveDatetime


class PatientDetail(PatientRead):
    visits: list["VisitRead"] = Field(default_factory=list)


class PatientListItem(PatientRead):
    last_visit_date: date | None = None


class PrescriptionItemBase(SQLModel):
    drug_name: str = Field(min_length=1, max_length=200)
    dosage: str | None = Field(default=None, max_length=200)
    days: int = Field(gt=0)
    note: str | None = None

    _strip_text = field_validator("drug_name", "dosage", "note", mode="before")(_strip)


class PrescriptionItem(PrescriptionItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    visit_id: int = Field(foreign_key="visit.id", index=True)


class PrescriptionItemWrite(PrescriptionItemBase):
    pass


class PrescriptionItemRead(PrescriptionItemBase):
    id: int


class VisitBase(SQLModel):
    visited_at: NaiveDatetime = Field(default_factory=datetime.now)
    symptoms: str | None = None
    diagnosis: str | None = None
    notes: str | None = None
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    temperature_c: float | None = Field(default=None, ge=30, le=45)
    blood_pressure: str | None = Field(default=None, max_length=20)
    fee: int = Field(default=0, ge=0)
    paid_amount: int = Field(default=0, ge=0)
    follow_up_date: date | None = None

    _strip_text = field_validator(
        "symptoms", "diagnosis", "notes", "blood_pressure", mode="before"
    )(_strip)


class Visit(VisitBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id", index=True)
    deleted_at: NaiveDatetime | None = None


class VisitWrite(VisitBase):
    items: list[PrescriptionItemWrite] = Field(default_factory=list)

    @model_validator(mode="after")
    def _paid_not_above_fee(self):
        if self.paid_amount > self.fee:
            raise ValueError("paid_amount cannot exceed fee")
        return self


class VisitRead(VisitBase):
    id: int
    patient_id: int
    deleted_at: NaiveDatetime | None = None
    items: list[PrescriptionItemRead] = Field(default_factory=list)


PatientDetail.model_rebuild()


class FollowUpRead(SQLModel):
    visit_id: int
    patient_id: int
    full_name: str
    phone: str | None
    follow_up_date: date


class RevenueRead(SQLModel):
    visit_count: int
    collected: int
    owed: int
