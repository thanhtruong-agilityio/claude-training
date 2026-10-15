from datetime import date, datetime
from typing import Literal

from pydantic import NaiveDatetime, field_validator
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
