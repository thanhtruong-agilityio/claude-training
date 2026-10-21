# Clinic App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use cl-core:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A local web app where one doctor records patients, visits, prescriptions and fees, and sees a revenue summary.

**Architecture:** New project `clinic-app/` next to `todo-app/`, same layout and tooling (FastAPI + SQLModel + SQLite backend, React + Vite + vitest frontend, docker compose, Makefile). `todo-app/` is read for patterns and never modified. Backend is built and tested first (patients, visits + prescription items, reports), then the frontend on top of that API.

**Tech Stack:** Python 3.12, FastAPI, SQLModel, uv, pytest, httpx; React 18, TypeScript, Vite, vitest, @testing-library/react.

**Spec:** `docs/specs/2026-10-15-clinic-app-design.md`

**Architecture Diagrams:** None generated.

## Global Constraints

Copied from the spec. Every task includes these.

- One user (the doctor). No login, no roles, no multi-user.
- Runs locally. FastAPI + React + SQLite. `todo-app/` is untouched.
- Money is an integer (VND). `fee` defaults to 0 and must be >= 0. `paid_amount` must be >= 0 and <= `fee`.
- Text fields are trimmed; empty or whitespace-only `full_name` and `drug_name` are rejected (422).
- `days` > 0. `sex` is one of `male`, `female`, `other`, or null. `birth_year` is between 1900 and the current year.
- `visited_at` is stored as local clinic time. Report `from`/`to` are dates, both inclusive.
- Visits are soft-deleted via `deleted_at`; prescription items are never deleted with it. No cascade delete.
- Patients are never hard-deleted; they are archived with `is_archived` and unarchived with `PATCH /patients/{id}`. Archived patients are hidden from search and follow-ups by default.
- Lists, "last visit date" and revenue reports exclude soft-deleted visits.
- Revenue is booked on the visit date (`visited_at`); paying a debt later edits `paid_amount`.
- New visit, edit or restore of a visit for an archived patient → 409. Restore of a non-deleted visit → 409.
- `GET /visits/follow-ups` must be matched before `GET /visits/{id}`.
- Bind to 127.0.0.1 only (no LAN-published docker ports), strict CORS, `make backup` target, no logging of request bodies.
- `*.db` stays in `.gitignore`. Never use real patient data in tests, commits or any AI tool: fake data only.
- Out of scope: appointment booking, printing/PDF, image upload, SMS, drug catalog, stock, multi-user.

## How This Plan Was Created

1. **Spec provided:** `docs/specs/2026-10-15-clinic-app-design.md`
2. **Implementation plan created:** This document
3. **Recommended execution:** `cl-core:executing-plans`

---

## Working agreements for the executor

- One ticket per branch named `<type>/<ticket>-<slug>`; never commit to `main`. The ticket id for this work was not provided: ask the user for it before Task 1 Step 1 and use it in the branch name (example: `feat/<ticket>-clinic-app`).
- `git status` in this repo already shows unrelated uncommitted `todo-app/` changes. Every commit below stages explicit paths under `clinic-app/` only. Never run `git add -A` or `git add .`.
- Commit subjects are lowercase Conventional Commits. Ask the user before any push or merge.
- Backend commands run from `clinic-app/backend`, frontend commands from `clinic-app/frontend`.

## File Structure

```
clinic-app/
  backend/
    pyproject.toml            deps + pytest config
    Dockerfile, .dockerignore copied from todo-app
    app/
      db.py                   engine (clinic.db) + session
      models.py               tables + request/response schemas + validators
      queries.py              load_visit_read(): visit + its items as VisitRead
      main.py                 app, CORS, router registration (order matters)
      routers/patients.py     /patients
      routers/visits.py       /patients/{id}/visits, /visits/{id}, delete, restore
      routers/reports.py      /visits/follow-ups, /reports/revenue
    tests/
      conftest.py             client + patient + visit factory fixtures
      test_patients.py, test_visits.py, test_reports.py
  frontend/
    package.json, tsconfig.json, vite.config.ts, index.html, Dockerfile, .dockerignore
    src/
      main.tsx, setupTests.ts, App.tsx (view switching, no router)
      types.ts, api.ts
      pages/PatientListPage.tsx, PatientRecordPage.tsx, RevenuePage.tsx
      components/VisitForm.tsx, FollowUps.tsx
      __tests__/
  docker-compose.yml, Makefile, README.md
```

---

### Task 1: Backend scaffold + patients API

**Files:**
- Create: `clinic-app/backend/pyproject.toml`, `Dockerfile`, `.dockerignore`
- Create: `clinic-app/backend/app/__init__.py`, `db.py`, `models.py`, `main.py`
- Create: `clinic-app/backend/app/routers/__init__.py`, `routers/patients.py`
- Create: `clinic-app/backend/tests/conftest.py`, `tests/test_patients.py`

**Interfaces:**
- Consumes: nothing.
- Produces (later tasks rely on these exact names):
  - `app.db`: `engine`, `init_db()`, `get_session()`
  - `app.models`: `Patient` (table: `id`, `full_name`, `birth_year`, `sex`, `phone`, `address`, `allergies`, `medical_history`, `is_archived`, `created_at`), `PatientCreate`, `PatientUpdate`, `PatientRead`, helper `_strip`
  - `app.routers.patients.router`
  - fixtures `client` and `patient` (a dict returned by `POST /patients`)

**Acceptance Criteria:**
- [ ] `POST /patients` creates (201), trims text, rejects blank name, bad `sex`, future `birth_year` (422).
- [ ] `GET /patients?q=` finds by name (case-insensitive, Vietnamese diacritics) or phone; hides archived unless `include_archived=true`.
- [ ] `GET /patients/{id}`, `PATCH /patients/{id}` (edit, archive, unarchive); unknown id → 404; `full_name: null` → 422.

- [ ] **Step 1: Create the branch and scaffold files**

```bash
git checkout -b feat/<ticket>-clinic-app   # replace <ticket> with the id the user gave
mkdir -p clinic-app/backend/app/routers clinic-app/backend/tests
cp todo-app/backend/Dockerfile todo-app/backend/.dockerignore clinic-app/backend/
touch clinic-app/backend/app/__init__.py clinic-app/backend/app/routers/__init__.py
```

Create `clinic-app/backend/pyproject.toml`:

```toml
[project]
name = "clinic-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "sqlmodel>=0.0.22",
    "uvicorn>=0.30",
]

[dependency-groups]
dev = [
    "pytest>=8",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

Create `clinic-app/backend/app/db.py`:

```python
from sqlmodel import Session, SQLModel, create_engine

engine = create_engine(
    "sqlite:///clinic.db", connect_args={"check_same_thread": False}
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Create `clinic-app/backend/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def patient(client):
    return client.post("/patients", json={"full_name": "Test Patient"}).json()
```

- [ ] **Step 2: Write the failing tests**

Create `clinic-app/backend/tests/test_patients.py`:

```python
def test_create_and_get(client):
    res = client.post(
        "/patients",
        json={"full_name": "  Nguyễn Văn A  ", "phone": " 0900000001 ", "sex": "male"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["full_name"] == "Nguyễn Văn A"
    assert body["phone"] == "0900000001"
    assert body["is_archived"] is False

    got = client.get(f"/patients/{body['id']}")
    assert got.status_code == 200
    assert got.json()["full_name"] == "Nguyễn Văn A"


def test_create_rejects_blank_name(client):
    assert client.post("/patients", json={"full_name": ""}).status_code == 422
    assert client.post("/patients", json={"full_name": "   "}).status_code == 422


def test_create_rejects_bad_sex_and_birth_year(client):
    assert client.post("/patients", json={"full_name": "A", "sex": "x"}).status_code == 422
    assert client.post("/patients", json={"full_name": "A", "birth_year": 1800}).status_code == 422
    assert client.post("/patients", json={"full_name": "A", "birth_year": 3000}).status_code == 422


def test_search_by_name_ignores_case_and_keeps_diacritics(client):
    client.post("/patients", json={"full_name": "Nguyễn Văn A"})
    client.post("/patients", json={"full_name": "Trần Thị B"})
    names = [p["full_name"] for p in client.get("/patients", params={"q": "nguyễn"}).json()]
    assert names == ["Nguyễn Văn A"]


def test_search_by_phone(client):
    client.post("/patients", json={"full_name": "A", "phone": "0900000001"})
    client.post("/patients", json={"full_name": "B", "phone": "0911111111"})
    names = [p["full_name"] for p in client.get("/patients", params={"q": "0911"}).json()]
    assert names == ["B"]


def test_archived_hidden_unless_requested(client, patient):
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    assert client.get("/patients").json() == []
    shown = client.get("/patients", params={"include_archived": True}).json()
    assert [p["id"] for p in shown] == [patient["id"]]


def test_patch_edits_and_unarchives(client, patient):
    pid = patient["id"]
    client.patch(f"/patients/{pid}", json={"is_archived": True})
    res = client.patch(f"/patients/{pid}", json={"is_archived": False, "allergies": "penicillin"})
    assert res.json()["is_archived"] is False
    assert res.json()["allergies"] == "penicillin"


def test_patch_rejects_null_or_blank_name(client, patient):
    pid = patient["id"]
    assert client.patch(f"/patients/{pid}", json={"full_name": None}).status_code == 422
    assert client.patch(f"/patients/{pid}", json={"full_name": "  "}).status_code == 422


def test_missing_patient_returns_404(client):
    assert client.get("/patients/999").status_code == 404
    assert client.patch("/patients/999", json={"phone": "1"}).status_code == 404
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd clinic-app/backend && uv sync && uv run pytest -v`
Expected: collection ERROR (`app.main` / `app.models` do not exist yet).

- [ ] **Step 4: Write the models**

Create `clinic-app/backend/app/models.py`:

```python
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
```

(Found while executing: the installed SQLModel rejects naive datetimes unless the field is typed `NaiveDatetime`. Every datetime field below uses it, which also matches the spec's "local clinic time".)

- [ ] **Step 5: Write the router and app**

Create `clinic-app/backend/app/routers/patients.py`:

```python
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
```

Create `clinic-app/backend/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import patients


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Clinic App", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(patients.router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd clinic-app/backend && uv run pytest -v`
Expected: all 9 tests in `test_patients.py` PASS.

- [ ] **Step 7: Commit**

```bash
git add clinic-app/backend
git commit -m "feat(clinic-app): add backend scaffold and patients api"
```

(`uv.lock` is created by `uv sync` and is included by `git add clinic-app/backend`; `*.db` and `.venv/` are ignored.)

---

### Task 2: Visits and prescription items API

**Files:**
- Modify: `clinic-app/backend/app/models.py` (append visit/item models; add patient detail/list schemas)
- Create: `clinic-app/backend/app/queries.py`
- Create: `clinic-app/backend/app/routers/visits.py`
- Modify: `clinic-app/backend/app/routers/patients.py` (detail with visits, list with last visit date)
- Modify: `clinic-app/backend/app/main.py` (register visits router)
- Modify: `clinic-app/backend/tests/conftest.py` (add `make_visit` fixture)
- Test: `clinic-app/backend/tests/test_visits.py`

**Interfaces:**
- Consumes: `Patient`, `PatientRead`, `_strip`, `get_session`, fixtures `client`, `patient` from Task 1.
- Produces:
  - `app.models`: `Visit` (table: `id`, `patient_id`, `visited_at`, `symptoms`, `diagnosis`, `notes`, `weight_kg`, `temperature_c`, `blood_pressure`, `fee`, `paid_amount`, `follow_up_date`, `deleted_at`), `PrescriptionItem` (table: `id`, `visit_id`, `drug_name`, `dosage`, `days`, `note`), `PrescriptionItemRead`, `VisitWrite` (create and PUT body, includes `items`), `VisitRead` (includes `items`), `PatientDetail` (`PatientRead` + `visits: list[VisitRead]`), `PatientListItem` (`PatientRead` + `last_visit_date: date | None`)
  - `app.queries.load_visit_read(session, visit) -> VisitRead`
  - `app.routers.visits.router`
  - fixture `make_visit(patient_id, **overrides) -> dict` (POSTs a visit, returns JSON)

**Acceptance Criteria:**
- [ ] `POST /patients/{id}/visits` saves a visit with its items in one request; any invalid item means nothing is saved.
- [ ] `GET /visits/{id}`, `PUT /visits/{id}` (replaces all items and fields), `DELETE /visits/{id}` (soft), `POST /visits/{id}/restore`.
- [ ] Validation and error codes exactly as in Global Constraints (422 / 404 / 409).
- [ ] `GET /patients/{id}` returns visits newest first, without deleted ones; `GET /patients` rows carry `last_visit_date` ignoring deleted visits.

- [ ] **Step 1: Add the fixture and write the failing tests**

Append to `clinic-app/backend/tests/conftest.py`:

```python
@pytest.fixture
def make_visit(client):
    def _make(patient_id, **overrides):
        body = {"symptoms": "cough", "fee": 100000, "paid_amount": 100000}
        body.update(overrides)
        res = client.post(f"/patients/{patient_id}/visits", json=body)
        assert res.status_code == 201, res.text
        return res.json()

    return _make
```

Create `clinic-app/backend/tests/test_visits.py`:

```python
def test_create_visit_with_items(client, patient, make_visit):
    visit = make_visit(
        patient["id"],
        items=[
            {"drug_name": "  Paracetamol  ", "dosage": "1 viên x 2", "days": 3},
            {"drug_name": "Vitamin C", "days": 5},
        ],
    )
    assert visit["patient_id"] == patient["id"]
    assert [i["drug_name"] for i in visit["items"]] == ["Paracetamol", "Vitamin C"]
    assert client.get(f"/visits/{visit['id']}").json()["items"][0]["days"] == 3


def test_invalid_item_saves_nothing(client, patient):
    res = client.post(
        f"/patients/{patient['id']}/visits",
        json={"items": [{"drug_name": "ok", "days": 1}, {"drug_name": "   ", "days": 1}]},
    )
    assert res.status_code == 422
    assert client.get(f"/patients/{patient['id']}").json()["visits"] == []


def test_visit_validation(client, patient):
    url = f"/patients/{patient['id']}/visits"
    assert client.post(url, json={"fee": -1}).status_code == 422
    assert client.post(url, json={"fee": 100, "paid_amount": 200}).status_code == 422
    assert client.post(url, json={"paid_amount": -5}).status_code == 422
    assert client.post(url, json={"items": [{"drug_name": "a", "days": 0}]}).status_code == 422


def test_fee_defaults_to_zero(client, patient):
    res = client.post(f"/patients/{patient['id']}/visits", json={})
    assert res.status_code == 201
    assert res.json()["fee"] == 0


def test_create_for_missing_patient_404(client):
    assert client.post("/patients/999/visits", json={}).status_code == 404


def test_create_for_archived_patient_409(client, patient):
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    assert client.post(f"/patients/{patient['id']}/visits", json={}).status_code == 409


def test_put_replaces_fields_and_items(client, patient, make_visit):
    visit = make_visit(patient["id"], fee=100000, paid_amount=0, items=[{"drug_name": "A", "days": 1}])
    res = client.put(
        f"/visits/{visit['id']}",
        json={
            "visited_at": visit["visited_at"],
            "fee": 100000,
            "paid_amount": 100000,
            "items": [{"drug_name": "B", "days": 2}],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["paid_amount"] == 100000
    assert body["visited_at"] == visit["visited_at"]
    assert [i["drug_name"] for i in body["items"]] == ["B"]


def test_put_archived_patient_409(client, patient, make_visit):
    visit = make_visit(patient["id"])
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    assert client.put(f"/visits/{visit['id']}", json={}).status_code == 409


def test_soft_delete_hides_visit_and_restore_brings_items_back(client, patient, make_visit):
    visit = make_visit(patient["id"], items=[{"drug_name": "A", "days": 1}])
    assert client.delete(f"/visits/{visit['id']}").status_code == 200

    assert client.get(f"/visits/{visit['id']}").status_code == 404
    assert client.get(f"/patients/{patient['id']}").json()["visits"] == []

    restored = client.post(f"/visits/{visit['id']}/restore")
    assert restored.status_code == 200
    assert restored.json()["deleted_at"] is None
    assert [i["drug_name"] for i in restored.json()["items"]] == ["A"]
    assert len(client.get(f"/patients/{patient['id']}").json()["visits"]) == 1


def test_restore_errors(client, patient, make_visit):
    visit = make_visit(patient["id"])
    assert client.post(f"/visits/{visit['id']}/restore").status_code == 409
    assert client.post("/visits/999/restore").status_code == 404

    client.delete(f"/visits/{visit['id']}")
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    assert client.post(f"/visits/{visit['id']}/restore").status_code == 409


def test_delete_missing_or_already_deleted_404(client, patient, make_visit):
    visit = make_visit(patient["id"])
    client.delete(f"/visits/{visit['id']}")
    assert client.delete(f"/visits/{visit['id']}").status_code == 404
    assert client.delete("/visits/999").status_code == 404


def test_patient_detail_visits_newest_first(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-01-01T09:00:00", symptoms="old")
    make_visit(patient["id"], visited_at="2026-03-01T09:00:00", symptoms="new")
    visits = client.get(f"/patients/{patient['id']}").json()["visits"]
    assert [v["symptoms"] for v in visits] == ["new", "old"]


def test_list_shows_last_visit_date_ignoring_deleted(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-01-01T09:00:00")
    latest = make_visit(patient["id"], visited_at="2026-03-01T09:00:00")
    row = client.get("/patients").json()[0]
    assert row["last_visit_date"] == "2026-03-01"

    client.delete(f"/visits/{latest['id']}")
    assert client.get("/patients").json()[0]["last_visit_date"] == "2026-01-01"


def test_list_last_visit_date_null_without_visits(client, patient):
    assert client.get("/patients").json()[0]["last_visit_date"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd clinic-app/backend && uv run pytest tests/test_visits.py -v`
Expected: FAIL (404 on `/patients/{id}/visits`, missing `visits` key).

- [ ] **Step 3: Add models**

Edit `clinic-app/backend/app/models.py`: change the first import line to `from datetime import date, datetime` (unchanged) and `from pydantic import field_validator, model_validator`, then append:

```python
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
```

- [ ] **Step 4: Add the query helper**

Create `clinic-app/backend/app/queries.py`:

```python
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
```

- [ ] **Step 5: Add the visits router**

Create `clinic-app/backend/app/routers/visits.py`:

```python
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

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
def create_visit(
    patient_id: int, data: VisitWrite, session: Session = Depends(get_session)
):
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
def update_visit(
    visit_id: int, data: VisitWrite, session: Session = Depends(get_session)
):
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
    visit.deleted_at = datetime.now()
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
```

- [ ] **Step 6: Update patients router and main**

In `clinic-app/backend/app/routers/patients.py` replace the imports and the `list_patients` / `get_patient` functions:

```python
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
```

```python
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
```

```python
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
```

`PatientRead` stays imported because `create_patient` and `update_patient` still use it. In `main.py` change the import to `from app.routers import patients, visits` and add `app.include_router(visits.router)` after the patients line.

- [ ] **Step 7: Run all tests**

Run: `cd clinic-app/backend && uv run pytest -v`
Expected: all tests in `test_patients.py` and `test_visits.py` PASS.

- [ ] **Step 8: Commit**

```bash
git add clinic-app/backend
git commit -m "feat(clinic-app): add visits, prescription items and soft delete"
```

---

### Task 3: Follow-ups and revenue reports

**Files:**
- Create: `clinic-app/backend/app/routers/reports.py`
- Modify: `clinic-app/backend/app/models.py` (append `FollowUpRead`, `RevenueRead`)
- Modify: `clinic-app/backend/app/main.py` (register reports router BEFORE visits router)
- Test: `clinic-app/backend/tests/test_reports.py`

**Interfaces:**
- Consumes: `Visit`, `Patient`, fixtures `client`, `patient`, `make_visit`.
- Produces:
  - `GET /visits/follow-ups?date=YYYY-MM-DD` (default today) → `list[FollowUpRead]` with fields `visit_id`, `patient_id`, `full_name`, `phone`, `follow_up_date`
  - `GET /reports/revenue?from=YYYY-MM-DD&to=YYYY-MM-DD` → `RevenueRead` with `visit_count`, `collected`, `owed` (all int)

**Acceptance Criteria:**
- [ ] Follow-ups list only non-deleted visits of non-archived patients due on that date; `/visits/follow-ups` is not shadowed by `/visits/{id}`.
- [ ] Revenue sums visits with `visited_at` between `from` and `to` inclusive, excluding deleted visits; `from` after `to` → 422.

- [ ] **Step 1: Write the failing tests**

Create `clinic-app/backend/tests/test_reports.py`:

```python
def test_follow_ups_route_is_not_shadowed_by_visit_id(client):
    res = client.get("/visits/follow-ups", params={"date": "2026-05-01"})
    assert res.status_code == 200
    assert res.json() == []


def test_follow_ups_lists_due_visits_only(client, patient, make_visit):
    due = make_visit(patient["id"], follow_up_date="2026-05-01")
    make_visit(patient["id"], follow_up_date="2026-05-02")
    gone = make_visit(patient["id"], follow_up_date="2026-05-01")
    client.delete(f"/visits/{gone['id']}")

    rows = client.get("/visits/follow-ups", params={"date": "2026-05-01"}).json()
    assert [r["visit_id"] for r in rows] == [due["id"]]
    assert rows[0]["full_name"] == "Test Patient"


def test_follow_ups_hide_archived_patients(client, patient, make_visit):
    make_visit(patient["id"], follow_up_date="2026-05-01")
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    assert client.get("/visits/follow-ups", params={"date": "2026-05-01"}).json() == []


def test_revenue_sums_inclusive_range_and_skips_deleted(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-05-01T08:00:00", fee=100000, paid_amount=100000)
    make_visit(patient["id"], visited_at="2026-05-02T23:30:00", fee=200000, paid_amount=50000)
    make_visit(patient["id"], visited_at="2026-05-03T00:00:00", fee=999, paid_amount=999)
    gone = make_visit(patient["id"], visited_at="2026-05-01T10:00:00", fee=500000, paid_amount=500000)
    client.delete(f"/visits/{gone['id']}")

    res = client.get("/reports/revenue", params={"from": "2026-05-01", "to": "2026-05-02"})
    assert res.status_code == 200
    assert res.json() == {"visit_count": 2, "collected": 150000, "owed": 150000}


def test_revenue_empty_range(client):
    res = client.get("/reports/revenue", params={"from": "2026-05-01", "to": "2026-05-01"})
    assert res.json() == {"visit_count": 0, "collected": 0, "owed": 0}


def test_revenue_rejects_reversed_range(client):
    res = client.get("/reports/revenue", params={"from": "2026-05-02", "to": "2026-05-01"})
    assert res.status_code == 422
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd clinic-app/backend && uv run pytest tests/test_reports.py -v`
Expected: FAIL (`/visits/follow-ups` returns 422 because it is parsed as a visit id; `/reports/revenue` returns 404).

- [ ] **Step 3: Add schemas**

Append to `clinic-app/backend/app/models.py`:

```python
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
```

- [ ] **Step 4: Add the reports router**

Create `clinic-app/backend/app/routers/reports.py`:

```python
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select

from app.db import get_session
from app.models import FollowUpRead, Patient, RevenueRead, Visit

router = APIRouter(tags=["reports"])


@router.get("/visits/follow-ups", response_model=list[FollowUpRead])
def follow_ups(
    on: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
):
    day = on or date.today()
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
```

- [ ] **Step 5: Register the router before visits**

In `clinic-app/backend/app/main.py` change the import to `from app.routers import patients, reports, visits` and register in this order, with the comment:

```python
app.include_router(patients.router)
# reports must come before visits: /visits/follow-ups would otherwise match /visits/{visit_id}
app.include_router(reports.router)
app.include_router(visits.router)
```

- [ ] **Step 6: Run all tests**

Run: `cd clinic-app/backend && uv run pytest -v`
Expected: all backend tests PASS.

- [ ] **Step 7: Commit**

```bash
git add clinic-app/backend
git commit -m "feat(clinic-app): add follow-ups and revenue reports"
```

---

### Task 4: Frontend scaffold + patient list page

**Files:**
- Create: `clinic-app/frontend/package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `Dockerfile`, `.dockerignore` (copied/adapted from todo-app)
- Create: `clinic-app/frontend/src/main.tsx`, `setupTests.ts`, `types.ts`, `api.ts`, `App.tsx`
- Create: `clinic-app/frontend/src/pages/PatientListPage.tsx`
- Test: `clinic-app/frontend/src/__tests__/PatientListPage.test.tsx`

**Interfaces:**
- Consumes: backend `GET/POST /patients` (Tasks 1-2).
- Produces:
  - `types.ts`: `Patient`, `PrescriptionItem`, `Visit`, `PatientDetail`, `VisitPayload`, `FollowUp`, `Revenue` (all defined in Step 3; later tasks only use these names)
  - `api.ts`: `listPatients(q?: string): Promise<Patient[]>`, `createPatient(data: NewPatient): Promise<Patient>`, `NewPatient`
  - `App.tsx`: `View = {name:"patients"} | {name:"patient"; id:number} | {name:"revenue"}`
  - `PatientListPage` props: `{ onOpen: (id: number) => void; onRevenue: () => void }`

**Acceptance Criteria:**
- [ ] Page lists patients (name, birth year, phone, last visit date), search box refetches with the query.
- [ ] "Add patient" form requires a non-blank name; blank/whitespace does not call the API.
- [ ] `npm test` and `npm run build` pass.

- [ ] **Step 1: Copy the scaffold**

```bash
mkdir -p clinic-app/frontend/src/{pages,components,__tests__}
cp todo-app/frontend/{tsconfig.json,vite.config.ts,index.html,Dockerfile,.dockerignore} clinic-app/frontend/
cp todo-app/frontend/src/setupTests.ts todo-app/frontend/src/main.tsx clinic-app/frontend/src/
sed -i '' 's/Todo/Clinic/g; s/todo/clinic/g' clinic-app/frontend/index.html
```

Create `clinic-app/frontend/package.json` (same as todo-app, new name):

```json
{
  "name": "clinic-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.1.0",
    "@types/node": "^22.20.5",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "jsdom": "^25.0.1",
    "typescript": "^5.6.3",
    "vite": "^5.4.11",
    "vitest": "^2.1.8"
  }
}
```

Run: `cd clinic-app/frontend && npm install`

- [ ] **Step 2: Write the failing test**

Create `clinic-app/frontend/src/__tests__/PatientListPage.test.tsx`:

```tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import PatientListPage from "../pages/PatientListPage";
import * as api from "../api";

vi.mock("../api");

const patients = [
  {
    id: 1, full_name: "Nguyen Van A", birth_year: 1980, sex: "male",
    phone: "0900000001", address: null, allergies: null, medical_history: null,
    is_archived: false, created_at: "2026-01-01T00:00:00", last_visit_date: "2026-03-01",
  },
];

beforeEach(() => {
  vi.mocked(api.listPatients).mockResolvedValue(patients);
  vi.mocked(api.createPatient).mockReset();
});

test("lists patients with last visit date", async () => {
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  expect(await screen.findByText("Nguyen Van A")).toBeInTheDocument();
  expect(screen.getByText("2026-03-01")).toBeInTheDocument();
});

test("opens a patient on click", async () => {
  const onOpen = vi.fn();
  render(<PatientListPage onOpen={onOpen} onRevenue={() => {}} />);
  fireEvent.click(await screen.findByText("Nguyen Van A"));
  expect(onOpen).toHaveBeenCalledWith(1);
});

test("search refetches with the query", async () => {
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  await screen.findByText("Nguyen Van A");
  fireEvent.change(screen.getByLabelText("Search"), { target: { value: "van" } });
  await waitFor(() => expect(api.listPatients).toHaveBeenLastCalledWith("van"));
});

test("blank name does not call the API", async () => {
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  await screen.findByText("Nguyen Van A");
  fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "   " } });
  fireEvent.click(screen.getByText("Add patient"));
  expect(api.createPatient).not.toHaveBeenCalled();
});

test("adds a patient with trimmed name and reloads", async () => {
  vi.mocked(api.createPatient).mockResolvedValue(patients[0]);
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  await screen.findByText("Nguyen Van A");
  fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "  Tran B  " } });
  fireEvent.change(screen.getByLabelText("Phone"), { target: { value: "0911" } });
  fireEvent.click(screen.getByText("Add patient"));
  await waitFor(() =>
    expect(api.createPatient).toHaveBeenCalledWith({ full_name: "Tran B", phone: "0911" }),
  );
});
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `cd clinic-app/frontend && npm test`
Expected: FAIL (cannot resolve `../pages/PatientListPage` / `../api`).

- [ ] **Step 4: Write types and api**

Create `clinic-app/frontend/src/types.ts`:

```ts
export interface Patient {
  id: number;
  full_name: string;
  birth_year: number | null;
  sex: string | null;
  phone: string | null;
  address: string | null;
  allergies: string | null;
  medical_history: string | null;
  is_archived: boolean;
  created_at: string;
  last_visit_date?: string | null;
}

export interface PrescriptionItem {
  id?: number;
  drug_name: string;
  dosage: string | null;
  days: number;
  note: string | null;
}

export interface Visit {
  id: number;
  patient_id: number;
  visited_at: string;
  symptoms: string | null;
  diagnosis: string | null;
  notes: string | null;
  weight_kg: number | null;
  temperature_c: number | null;
  blood_pressure: string | null;
  fee: number;
  paid_amount: number;
  follow_up_date: string | null;
  deleted_at: string | null;
  items: PrescriptionItem[];
}

export interface PatientDetail extends Patient {
  visits: Visit[];
}

export type VisitPayload = Omit<Visit, "id" | "patient_id" | "deleted_at" | "visited_at"> & {
  visited_at?: string;
};

export interface FollowUp {
  visit_id: number;
  patient_id: number;
  full_name: string;
  phone: string | null;
  follow_up_date: string;
}

export interface Revenue {
  visit_count: number;
  collected: number;
  owed: number;
}
```

Create `clinic-app/frontend/src/api.ts`:

```ts
import type { Patient } from "./types";

const BASE = "/api";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export type NewPatient = Partial<Omit<Patient, "id" | "is_archived" | "created_at">> & {
  full_name: string;
};

export const listPatients = (q?: string) =>
  request<Patient[]>(`${BASE}/patients${q ? `?q=${encodeURIComponent(q)}` : ""}`);

export const createPatient = (data: NewPatient) =>
  request<Patient>(`${BASE}/patients`, { method: "POST", body: JSON.stringify(data) });
```

- [ ] **Step 5: Write the page and App**

Create `clinic-app/frontend/src/pages/PatientListPage.tsx`:

```tsx
import { useCallback, useEffect, useState, type FormEvent } from "react";
import { createPatient, listPatients } from "../api";
import type { Patient } from "../types";

interface Props {
  onOpen: (id: number) => void;
  onRevenue: () => void;
}

export default function PatientListPage({ onOpen, onRevenue }: Props) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [query, setQuery] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const load = useCallback(() => {
    listPatients(query.trim() || undefined).then(setPatients);
  }, [query]);

  useEffect(load, [load]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const full_name = name.trim();
    if (!full_name) return;
    const trimmedPhone = phone.trim();
    await createPatient(trimmedPhone ? { full_name, phone: trimmedPhone } : { full_name });
    setName("");
    setPhone("");
    load();
  };

  return (
    <main>
      <h1>Patients</h1>
      <button onClick={onRevenue}>Revenue</button>

      <label>
        Search
        <input value={query} onChange={(e) => setQuery(e.target.value)} />
      </label>

      <form onSubmit={submit}>
        <label>
          Full name
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          Phone
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        <button type="submit">Add patient</button>
      </form>

      {patients.length === 0 ? (
        <p>No patients yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Birth year</th>
              <th>Phone</th>
              <th>Last visit</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.id}>
                <td>
                  <a href="#" onClick={(e) => { e.preventDefault(); onOpen(p.id); }}>
                    {p.full_name}
                  </a>
                </td>
                <td>{p.birth_year ?? ""}</td>
                <td>{p.phone ?? ""}</td>
                <td>{p.last_visit_date ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
```

Create `clinic-app/frontend/src/App.tsx`:

```tsx
import { useState } from "react";
import PatientListPage from "./pages/PatientListPage";

export type View =
  | { name: "patients" }
  | { name: "patient"; id: number }
  | { name: "revenue" };

export default function App() {
  const [view, setView] = useState<View>({ name: "patients" });

  return (
    <PatientListPage
      onOpen={(id) => setView({ name: "patient", id })}
      onRevenue={() => setView({ name: "revenue" })}
    />
  );
}
```

(`view` is wired to the other pages in Tasks 5 and 6; `noUnusedLocals` is not enabled in `tsconfig.json`, so the build passes.)

- [ ] **Step 6: Run tests and build**

Run: `cd clinic-app/frontend && npm test && npm run build`
Expected: 5 tests PASS; build succeeds with no TypeScript errors.

- [ ] **Step 7: Commit**

```bash
git add clinic-app/frontend
git commit -m "feat(clinic-app): add frontend scaffold and patient list page"
```

(`node_modules/` and `dist/` are ignored by `.gitignore`.)

---

### Task 5: Patient record page + visit form

**Files:**
- Modify: `clinic-app/frontend/src/api.ts` (add `getPatient`, `createVisit`, `updateVisit`, `deleteVisit`)
- Create: `clinic-app/frontend/src/components/VisitForm.tsx`
- Create: `clinic-app/frontend/src/pages/PatientRecordPage.tsx`
- Modify: `clinic-app/frontend/src/App.tsx` (render record page)
- Test: `clinic-app/frontend/src/__tests__/VisitForm.test.tsx`

**Interfaces:**
- Consumes: `Patient`, `PatientDetail`, `Visit`, `VisitPayload` from `types.ts`; `request`, `BASE` in `api.ts`; backend visit endpoints (Task 2).
- Produces:
  - `api.ts`: `getPatient(id: number): Promise<PatientDetail>`, `createVisit(patientId: number, data: VisitPayload): Promise<Visit>`, `updateVisit(id: number, data: VisitPayload): Promise<Visit>`, `deleteVisit(id: number): Promise<unknown>`
  - `VisitForm` props: `{ initial?: Visit; onSubmit: (data: VisitPayload) => void; onCancel: () => void }`
  - `PatientRecordPage` props: `{ id: number; onBack: () => void }`

**Acceptance Criteria:**
- [ ] Visit form has symptoms/diagnosis/notes, vitals, prescription rows (add/remove), fee, paid, follow-up date; saves everything in one `onSubmit` call.
- [ ] Blank prescription rows are dropped before submit; `paid > fee` shows an error and does not submit.
- [ ] Record page highlights allergies/medical history, lists visits newest first, supports new visit, edit visit (re-uses the form, sends original `visited_at`) and delete visit.

- [ ] **Step 1: Write the failing test**

Create `clinic-app/frontend/src/__tests__/VisitForm.test.tsx`:

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import VisitForm from "../components/VisitForm";

function fill(label: string, value: string, index = 0) {
  fireEvent.change(screen.getAllByLabelText(label)[index], { target: { value } });
}

test("adds and removes prescription rows", () => {
  render(<VisitForm onSubmit={() => {}} onCancel={() => {}} />);
  expect(screen.getAllByLabelText("Drug name")).toHaveLength(1);
  fireEvent.click(screen.getByText("Add drug"));
  expect(screen.getAllByLabelText("Drug name")).toHaveLength(2);
  fireEvent.click(screen.getAllByText("Remove")[0]);
  expect(screen.getAllByLabelText("Drug name")).toHaveLength(1);
});

test("submits one payload and drops blank prescription rows", () => {
  const onSubmit = vi.fn();
  render(<VisitForm onSubmit={onSubmit} onCancel={() => {}} />);
  fill("Symptoms", "  cough ");
  fill("Fee", "100000");
  fill("Paid", "50000");
  fill("Drug name", " Paracetamol ");
  fill("Days", "3");
  fireEvent.click(screen.getByText("Add drug"));
  fill("Drug name", "   ", 1);
  fireEvent.click(screen.getByText("Save visit"));

  expect(onSubmit).toHaveBeenCalledTimes(1);
  const payload = onSubmit.mock.calls[0][0];
  expect(payload.symptoms).toBe("cough");
  expect(payload.fee).toBe(100000);
  expect(payload.paid_amount).toBe(50000);
  expect(payload.items).toEqual([
    { drug_name: "Paracetamol", dosage: null, days: 3, note: null },
  ]);
});

test("paid above fee shows an error and does not submit", () => {
  const onSubmit = vi.fn();
  render(<VisitForm onSubmit={onSubmit} onCancel={() => {}} />);
  fill("Fee", "100");
  fill("Paid", "200");
  fireEvent.click(screen.getByText("Save visit"));
  expect(screen.getByText("Paid cannot exceed fee")).toBeInTheDocument();
  expect(onSubmit).not.toHaveBeenCalled();
});

test("edit keeps the original visit time", () => {
  const onSubmit = vi.fn();
  const initial = {
    id: 1, patient_id: 1, visited_at: "2026-03-01T09:00:00", symptoms: "old",
    diagnosis: null, notes: null, weight_kg: null, temperature_c: null,
    blood_pressure: null, fee: 100, paid_amount: 0, follow_up_date: null,
    deleted_at: null, items: [{ id: 5, drug_name: "A", dosage: null, days: 2, note: null }],
  };
  render(<VisitForm initial={initial} onSubmit={onSubmit} onCancel={() => {}} />);
  fill("Paid", "100");
  fireEvent.click(screen.getByText("Save visit"));
  expect(onSubmit.mock.calls[0][0].visited_at).toBe("2026-03-01T09:00:00");
  expect(onSubmit.mock.calls[0][0].items[0].drug_name).toBe("A");
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd clinic-app/frontend && npm test -- VisitForm`
Expected: FAIL (cannot resolve `../components/VisitForm`).

- [ ] **Step 3: Extend the api**

Append to `clinic-app/frontend/src/api.ts` (and extend the type import to `import type { Patient, PatientDetail, Visit, VisitPayload } from "./types";`):

```ts
export const getPatient = (id: number) => request<PatientDetail>(`${BASE}/patients/${id}`);

export const createVisit = (patientId: number, data: VisitPayload) =>
  request<Visit>(`${BASE}/patients/${patientId}/visits`, {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateVisit = (id: number, data: VisitPayload) =>
  request<Visit>(`${BASE}/visits/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const deleteVisit = (id: number) =>
  request<unknown>(`${BASE}/visits/${id}`, { method: "DELETE" });
```

- [ ] **Step 4: Write the visit form**

Create `clinic-app/frontend/src/components/VisitForm.tsx`:

```tsx
import { useState, type FormEvent } from "react";
import type { Visit, VisitPayload } from "../types";

interface Row {
  drug_name: string;
  dosage: string;
  days: string;
  note: string;
}

interface Props {
  initial?: Visit;
  onSubmit: (data: VisitPayload) => void;
  onCancel: () => void;
}

const emptyRow = (): Row => ({ drug_name: "", dosage: "", days: "1", note: "" });
const orNull = (s: string) => (s.trim() ? s.trim() : null);
const numOrNull = (s: string) => (s.trim() ? Number(s) : null);

export default function VisitForm({ initial, onSubmit, onCancel }: Props) {
  const [symptoms, setSymptoms] = useState(initial?.symptoms ?? "");
  const [diagnosis, setDiagnosis] = useState(initial?.diagnosis ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [weight, setWeight] = useState(String(initial?.weight_kg ?? ""));
  const [temp, setTemp] = useState(String(initial?.temperature_c ?? ""));
  const [bp, setBp] = useState(initial?.blood_pressure ?? "");
  const [fee, setFee] = useState(String(initial?.fee ?? ""));
  const [paid, setPaid] = useState(String(initial?.paid_amount ?? ""));
  const [followUp, setFollowUp] = useState(initial?.follow_up_date ?? "");
  const [rows, setRows] = useState<Row[]>(
    initial?.items.length
      ? initial.items.map((i) => ({
          drug_name: i.drug_name,
          dosage: i.dosage ?? "",
          days: String(i.days),
          note: i.note ?? "",
        }))
      : [emptyRow()],
  );
  const [error, setError] = useState("");

  const setRow = (index: number, patch: Partial<Row>) =>
    setRows((rs) => rs.map((r, i) => (i === index ? { ...r, ...patch } : r)));

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const feeValue = Number(fee || 0);
    const paidValue = Number(paid || 0);
    if (paidValue > feeValue) {
      setError("Paid cannot exceed fee");
      return;
    }
    setError("");
    onSubmit({
      ...(initial ? { visited_at: initial.visited_at } : {}),
      symptoms: orNull(symptoms),
      diagnosis: orNull(diagnosis),
      notes: orNull(notes),
      weight_kg: numOrNull(weight),
      temperature_c: numOrNull(temp),
      blood_pressure: orNull(bp),
      fee: feeValue,
      paid_amount: paidValue,
      follow_up_date: followUp || null,
      items: rows
        .filter((r) => r.drug_name.trim())
        .map((r) => ({
          drug_name: r.drug_name.trim(),
          dosage: orNull(r.dosage),
          days: Number(r.days || 1),
          note: orNull(r.note),
        })),
    });
  };

  return (
    <form onSubmit={submit}>
      <label>Symptoms <textarea value={symptoms} onChange={(e) => setSymptoms(e.target.value)} /></label>
      <label>Diagnosis <textarea value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} /></label>
      <label>Notes <textarea value={notes} onChange={(e) => setNotes(e.target.value)} /></label>

      <label>Weight (kg) <input value={weight} onChange={(e) => setWeight(e.target.value)} /></label>
      <label>Temperature (°C) <input value={temp} onChange={(e) => setTemp(e.target.value)} /></label>
      <label>Blood pressure <input value={bp} onChange={(e) => setBp(e.target.value)} /></label>

      <h3>Prescription</h3>
      {rows.map((row, i) => (
        <div key={i}>
          <label>Drug name <input value={row.drug_name} onChange={(e) => setRow(i, { drug_name: e.target.value })} /></label>
          <label>Dosage <input value={row.dosage} onChange={(e) => setRow(i, { dosage: e.target.value })} /></label>
          <label>Days <input value={row.days} onChange={(e) => setRow(i, { days: e.target.value })} /></label>
          <label>Drug note <input value={row.note} onChange={(e) => setRow(i, { note: e.target.value })} /></label>
          <button type="button" onClick={() => setRows((rs) => rs.filter((_, j) => j !== i))}>
            Remove
          </button>
        </div>
      ))}
      <button type="button" onClick={() => setRows((rs) => [...rs, emptyRow()])}>
        Add drug
      </button>

      <label>Fee <input value={fee} onChange={(e) => setFee(e.target.value)} /></label>
      <label>Paid <input value={paid} onChange={(e) => setPaid(e.target.value)} /></label>
      <label>Follow-up date <input type="date" value={followUp} onChange={(e) => setFollowUp(e.target.value)} /></label>

      {error && <p role="alert">{error}</p>}
      <button type="submit">Save visit</button>
      <button type="button" onClick={onCancel}>Cancel</button>
    </form>
  );
}
```

Note: the test label `Drug name` must match only the drug-name input; the note input is labelled `Drug note` so `getAllByLabelText("Drug name")` stays unambiguous.

- [ ] **Step 5: Write the record page and wire it into App**

Create `clinic-app/frontend/src/pages/PatientRecordPage.tsx`:

```tsx
import { useCallback, useEffect, useState } from "react";
import { createVisit, deleteVisit, getPatient, updateVisit } from "../api";
import VisitForm from "../components/VisitForm";
import type { PatientDetail, Visit, VisitPayload } from "../types";

interface Props {
  id: number;
  onBack: () => void;
}

type Mode = { name: "view" } | { name: "new" } | { name: "edit"; visit: Visit };

export default function PatientRecordPage({ id, onBack }: Props) {
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [mode, setMode] = useState<Mode>({ name: "view" });

  const load = useCallback(() => {
    getPatient(id).then(setPatient);
  }, [id]);

  useEffect(load, [load]);

  const save = async (data: VisitPayload) => {
    if (mode.name === "edit") await updateVisit(mode.visit.id, data);
    else await createVisit(id, data);
    setMode({ name: "view" });
    load();
  };

  const remove = async (visitId: number) => {
    await deleteVisit(visitId);
    load();
  };

  if (!patient) return <p>Loading…</p>;

  return (
    <main>
      <button onClick={onBack}>Back</button>
      <h1>{patient.full_name}</h1>
      <p>
        {patient.birth_year ?? "?"} · {patient.sex ?? "?"} · {patient.phone ?? ""} · {patient.address ?? ""}
      </p>
      {(patient.allergies || patient.medical_history) && (
        <section style={{ background: "#fde8e8", padding: "0.5rem" }}>
          {patient.allergies && <p><strong>Allergies:</strong> {patient.allergies}</p>}
          {patient.medical_history && <p><strong>History:</strong> {patient.medical_history}</p>}
        </section>
      )}

      {mode.name === "view" ? (
        <button onClick={() => setMode({ name: "new" })}>New visit</button>
      ) : (
        <VisitForm
          initial={mode.name === "edit" ? mode.visit : undefined}
          onSubmit={save}
          onCancel={() => setMode({ name: "view" })}
        />
      )}

      <h2>Visits</h2>
      {patient.visits.length === 0 && <p>No visits yet.</p>}
      {patient.visits.map((v) => (
        <article key={v.id}>
          <h3>{v.visited_at.slice(0, 10)}</h3>
          <p>{v.symptoms} {v.diagnosis && `→ ${v.diagnosis}`}</p>
          <ul>
            {v.items.map((i) => (
              <li key={i.id}>{i.drug_name} — {i.dosage ?? ""} × {i.days} days</li>
            ))}
          </ul>
          <p>Fee {v.fee} · Paid {v.paid_amount}{v.paid_amount < v.fee ? ` · Owed ${v.fee - v.paid_amount}` : ""}</p>
          <button onClick={() => setMode({ name: "edit", visit: v })}>Edit</button>
          <button onClick={() => remove(v.id)}>Delete</button>
        </article>
      ))}
    </main>
  );
}
```

Replace the body of `clinic-app/frontend/src/App.tsx`:

```tsx
import { useState } from "react";
import PatientListPage from "./pages/PatientListPage";
import PatientRecordPage from "./pages/PatientRecordPage";

export type View =
  | { name: "patients" }
  | { name: "patient"; id: number }
  | { name: "revenue" };

export default function App() {
  const [view, setView] = useState<View>({ name: "patients" });

  if (view.name === "patient") {
    return <PatientRecordPage id={view.id} onBack={() => setView({ name: "patients" })} />;
  }

  return (
    <PatientListPage
      onOpen={(id) => setView({ name: "patient", id })}
      onRevenue={() => setView({ name: "revenue" })}
    />
  );
}
```

- [ ] **Step 6: Run tests and build**

Run: `cd clinic-app/frontend && npm test && npm run build`
Expected: all frontend tests PASS (list page + 4 visit form tests); build succeeds.

- [ ] **Step 7: Commit**

```bash
git add clinic-app/frontend
git commit -m "feat(clinic-app): add patient record page and visit form"
```

---

### Task 6: Revenue page and today's follow-ups

**Files:**
- Modify: `clinic-app/frontend/src/api.ts` (add `listFollowUps`, `getRevenue`)
- Create: `clinic-app/frontend/src/components/FollowUps.tsx`
- Create: `clinic-app/frontend/src/pages/RevenuePage.tsx`
- Modify: `clinic-app/frontend/src/pages/PatientListPage.tsx` (render `<FollowUps />` at the top)
- Modify: `clinic-app/frontend/src/App.tsx` (render revenue page)
- Modify: `clinic-app/frontend/src/__tests__/PatientListPage.test.tsx` (mock `listFollowUps`)
- Test: `clinic-app/frontend/src/__tests__/RevenuePage.test.tsx`, `FollowUps.test.tsx`

**Interfaces:**
- Consumes: `FollowUp`, `Revenue` from `types.ts`; backend reports (Task 3).
- Produces:
  - `api.ts`: `listFollowUps(date?: string): Promise<FollowUp[]>`, `getRevenue(from: string, to: string): Promise<Revenue>`
  - `FollowUps` props: `{ onOpen: (patientId: number) => void }`
  - `RevenuePage` props: `{ onBack: () => void }`

**Acceptance Criteria:**
- [ ] Home page shows today's follow-ups above the patient list; clicking one opens that patient.
- [ ] Revenue page: pick a from/to date (both default to today), shows visit count, collected, owed.

- [ ] **Step 1: Write the failing tests**

Create `clinic-app/frontend/src/__tests__/FollowUps.test.tsx`:

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import FollowUps from "../components/FollowUps";
import * as api from "../api";

vi.mock("../api");

test("shows nothing when no follow-ups", async () => {
  vi.mocked(api.listFollowUps).mockResolvedValue([]);
  render(<FollowUps onOpen={() => {}} />);
  await Promise.resolve();
  expect(screen.queryByText("Follow-ups today")).not.toBeInTheDocument();
});

test("lists follow-ups and opens the patient", async () => {
  vi.mocked(api.listFollowUps).mockResolvedValue([
    { visit_id: 7, patient_id: 3, full_name: "Tran B", phone: "0911", follow_up_date: "2026-05-01" },
  ]);
  const onOpen = vi.fn();
  render(<FollowUps onOpen={onOpen} />);
  expect(await screen.findByText("Follow-ups today")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Tran B"));
  expect(onOpen).toHaveBeenCalledWith(3);
});
```

Create `clinic-app/frontend/src/__tests__/RevenuePage.test.tsx`:

```tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import RevenuePage from "../pages/RevenuePage";
import * as api from "../api";

vi.mock("../api");

test("shows totals for the chosen range", async () => {
  vi.mocked(api.getRevenue).mockResolvedValue({ visit_count: 2, collected: 150000, owed: 150000 });
  render(<RevenuePage onBack={() => {}} />);

  fireEvent.change(screen.getByLabelText("From"), { target: { value: "2026-05-01" } });
  fireEvent.change(screen.getByLabelText("To"), { target: { value: "2026-05-02" } });

  await waitFor(() =>
    expect(api.getRevenue).toHaveBeenLastCalledWith("2026-05-01", "2026-05-02"),
  );
  expect(await screen.findByText("Visits: 2")).toBeInTheDocument();
  expect(screen.getByText("Collected: 150000")).toBeInTheDocument();
  expect(screen.getByText("Owed: 150000")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd clinic-app/frontend && npm test -- FollowUps RevenuePage`
Expected: FAIL (cannot resolve the new modules).

- [ ] **Step 3: Extend the api**

Append to `clinic-app/frontend/src/api.ts` (and extend the type import with `FollowUp, Revenue`):

```ts
export const listFollowUps = (date?: string) =>
  request<FollowUp[]>(`${BASE}/visits/follow-ups${date ? `?date=${date}` : ""}`);

export const getRevenue = (from: string, to: string) =>
  request<Revenue>(`${BASE}/reports/revenue?from=${from}&to=${to}`);
```

- [ ] **Step 4: Write the components**

Create `clinic-app/frontend/src/components/FollowUps.tsx`:

```tsx
import { useEffect, useState } from "react";
import { listFollowUps } from "../api";
import type { FollowUp } from "../types";

export default function FollowUps({ onOpen }: { onOpen: (patientId: number) => void }) {
  const [rows, setRows] = useState<FollowUp[]>([]);

  useEffect(() => {
    listFollowUps().then(setRows);
  }, []);

  if (rows.length === 0) return null;

  return (
    <section>
      <h2>Follow-ups today</h2>
      <ul>
        {rows.map((r) => (
          <li key={r.visit_id}>
            <a href="#" onClick={(e) => { e.preventDefault(); onOpen(r.patient_id); }}>
              {r.full_name}
            </a>{" "}
            {r.phone ?? ""}
          </li>
        ))}
      </ul>
    </section>
  );
}
```

Create `clinic-app/frontend/src/pages/RevenuePage.tsx`:

```tsx
import { useEffect, useState } from "react";
import { getRevenue } from "../api";
import type { Revenue } from "../types";

const today = () => new Date().toLocaleDateString("sv-SE"); // YYYY-MM-DD, local time

export default function RevenuePage({ onBack }: { onBack: () => void }) {
  const [from, setFrom] = useState(today());
  const [to, setTo] = useState(today());
  const [revenue, setRevenue] = useState<Revenue | null>(null);

  useEffect(() => {
    if (!from || !to || from > to) return;
    getRevenue(from, to).then(setRevenue);
  }, [from, to]);

  return (
    <main>
      <button onClick={onBack}>Back</button>
      <h1>Revenue</h1>
      <label>From <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} /></label>
      <label>To <input type="date" value={to} onChange={(e) => setTo(e.target.value)} /></label>
      {from > to && <p role="alert">From must not be after To</p>}
      {revenue && (
        <ul>
          <li>Visits: {revenue.visit_count}</li>
          <li>Collected: {revenue.collected}</li>
          <li>Owed: {revenue.owed}</li>
        </ul>
      )}
    </main>
  );
}
```

- [ ] **Step 5: Wire into the list page, App and the existing list test**

In `clinic-app/frontend/src/pages/PatientListPage.tsx` add `import FollowUps from "../components/FollowUps";` and render `<FollowUps onOpen={onOpen} />` directly under the `<button onClick={onRevenue}>Revenue</button>` line.

In `clinic-app/frontend/src/__tests__/PatientListPage.test.tsx` add inside `beforeEach`:

```tsx
  vi.mocked(api.listFollowUps).mockResolvedValue([]);
```

In `clinic-app/frontend/src/App.tsx` add `import RevenuePage from "./pages/RevenuePage";` and, after the `patient` branch:

```tsx
  if (view.name === "revenue") {
    return <RevenuePage onBack={() => setView({ name: "patients" })} />;
  }
```

- [ ] **Step 6: Run tests and build**

Run: `cd clinic-app/frontend && npm test && npm run build`
Expected: all frontend tests PASS; build succeeds.

- [ ] **Step 7: Commit**

```bash
git add clinic-app/frontend
git commit -m "feat(clinic-app): add revenue page and today's follow-ups"
```

---

### Task 7: Docker, Makefile, backup and README

**Files:**
- Create: `clinic-app/docker-compose.yml`, `clinic-app/Makefile`, `clinic-app/README.md`

**Interfaces:**
- Consumes: both Dockerfiles from Tasks 1 and 4.
- Produces: `make up`, `make down`, `make logs`, `make test`, `make backup`.

**Acceptance Criteria:**
- [ ] Ports are published on 127.0.0.1 only.
- [ ] `make backup` writes `backups/clinic-<timestamp>.db`, which stays untracked.
- [ ] `make test` runs backend and frontend tests in containers.
- [ ] README states run, test, backup and data-safety rules.

- [ ] **Step 1: Write the files**

Create `clinic-app/docker-compose.yml`:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - ./backend:/app
      - /app/.venv

  frontend:
    build: ./frontend
    ports:
      - "127.0.0.1:5173:5173"
    environment:
      API_PROXY_TARGET: http://backend:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
```

Create `clinic-app/Makefile` (recipe lines are indented with a TAB):

```make
.PHONY: up down logs test test-backend test-frontend backup

up: ## build and start BE (:8000) + FE (:5173), localhost only
	docker compose up --build

down: ## stop and remove containers
	docker compose down

logs: ## follow logs
	docker compose logs -f

test: test-backend test-frontend ## run all tests in containers

test-backend:
	docker compose run --rm --no-deps backend uv run pytest

test-frontend:
	docker compose run --rm --no-deps frontend npm test

backup: ## copy the database to backups/clinic-<timestamp>.db
	@mkdir -p backups
	cp backend/clinic.db backups/clinic-$$(date +%Y%m%d-%H%M%S).db
```

Create `clinic-app/README.md`:

```markdown
# Clinic app

Local web app for a doctor running a small private clinic at home: patients, visits, prescriptions, fees, revenue summary. Design: `docs/specs/2026-10-15-clinic-app-design.md`.

## Run

- `make up`, then open http://localhost:5173 (API on http://localhost:8000).
- `make test` runs backend (pytest) and frontend (vitest) tests in containers.

## Backup

All records live in one SQLite file: `backend/clinic.db`.

- `make backup` copies it to `backups/clinic-<timestamp>.db`. Run it regularly and copy the result to a second disk.
- Keep this folder out of synced folders (iCloud, Dropbox) and turn on disk encryption (FileVault).

## Data safety

- There is no login. The app only listens on 127.0.0.1; never publish its ports to the network.
- `*.db` is gitignored. Never commit the database, and never use real patient data in tests or in any AI tool.
- Request bodies containing patient data must not be logged.

## Notes

- Revenue is booked on the visit date. Recording a later payment edits the visit's `paid_amount`, so earlier days' totals change.
- Deleting a visit hides it (soft delete); it can be restored via the API (`POST /visits/{id}/restore`).
```

- [ ] **Step 2: Verify**

Run: `cd clinic-app && make test`
Expected: backend and frontend tests PASS in containers (requires Docker running).

Run: `cd clinic-app && make up` in one terminal, then in another:
`curl -s -X POST localhost:8000/patients -H 'Content-Type: application/json' -d '{"full_name":"Demo Patient"}'`
Expected: JSON with `"id":1`. Open http://localhost:5173, see the patient, add a visit with a drug and a fee, open Revenue and check totals.

Run: `make backup && ls backups/ && git status --short backups backend/clinic.db`
Expected: one `clinic-*.db` file listed; `git status` prints nothing for `backups` and `clinic.db` (ignored).

Delete the demo data afterwards: `rm backend/clinic.db` (it only contains the fake patient).

- [ ] **Step 3: Commit**

```bash
git add clinic-app/docker-compose.yml clinic-app/Makefile clinic-app/README.md
git commit -m "feat(clinic-app): add docker compose, makefile, backup and readme"
```

---

## Self-Review

**Spec coverage**
- Data model, validation, trimming, defaults: Tasks 1-2 (models, tests).
- Soft delete + restore, items kept, 404/409 rules: Task 2.
- Archive/unarchive, hidden from search and follow-ups: Tasks 1 and 3.
- Follow-ups and route order: Task 3 (test + registration order comment).
- Revenue by visit date, inclusive range, deleted excluded: Task 3.
- Screens 1-4: Tasks 4 (list), 5 (record + visit form), 6 (revenue, follow-ups).
- Blank prescription rows dropped by UI: Task 5.
- Localhost bind, CORS, backup, no body logging, `.gitignore`: Task 7 plus existing CORS in Task 1 `main.py`.
- No gaps found.

**Placeholder scan:** none; every code step has full code. The only value left to the executor is the ticket id, which the plan says to ask the user for.

**Type consistency:** `VisitWrite`/`VisitRead`/`PatientDetail`/`PatientListItem`/`FollowUpRead`/`RevenueRead` match across models, routers and `types.ts`. `load_visit_read(session, visit)` is called with that signature in `visits.py` and `patients.py`. `listPatients(q?)`, `createVisit(patientId, data)`, `getRevenue(from, to)` match their call sites and tests.

**Spec deviation to confirm with the user:** the spec says `sex` may be "empty"; the plan stores that as `null` (an empty string is rejected with 422).
