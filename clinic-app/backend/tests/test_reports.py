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
    gone = make_visit(
        patient["id"], visited_at="2026-05-01T10:00:00", fee=500000, paid_amount=500000
    )
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
