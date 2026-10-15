import datetime as dt
import time

import pytest
import time_machine

# 18:00 UTC on 14 Oct is 01:00 on 15 Oct in Asia/Ho_Chi_Minh (UTC+7).
UTC_INSTANT = dt.datetime(2026, 10, 14, 18, 0, tzinfo=dt.timezone.utc)
CLINIC_DAY = "2026-10-15"


@pytest.fixture
def container_utc(monkeypatch):
    """The backend container has no TZ set, so it runs in UTC."""
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


def test_visit_booked_at_01_00_local_gets_local_date(client, patient, container_utc):
    with time_machine.travel(UTC_INSTANT, tick=False):
        res = client.post(f"/patients/{patient['id']}/visits", json={})
    assert res.status_code == 201
    assert res.json()["visited_at"].startswith(CLINIC_DAY)


def test_follow_ups_default_to_local_today(client, patient, make_visit, container_utc):
    make_visit(patient["id"], follow_up_date=CLINIC_DAY)
    with time_machine.travel(UTC_INSTANT, tick=False):
        res = client.get("/visits/follow-ups")
    assert [f["patient_id"] for f in res.json()] == [patient["id"]]
