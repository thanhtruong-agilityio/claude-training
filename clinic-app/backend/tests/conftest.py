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


@pytest.fixture
def make_visit(client):
    def _make(patient_id, **overrides):
        body = {"symptoms": "cough", "fee": 100000, "paid_amount": 100000}
        body.update(overrides)
        res = client.post(f"/patients/{patient_id}/visits", json=body)
        assert res.status_code == 201, res.text
        return res.json()

    return _make
