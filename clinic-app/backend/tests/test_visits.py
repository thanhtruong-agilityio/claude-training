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
    visit = make_visit(
        patient["id"], fee=100000, paid_amount=0, items=[{"drug_name": "A", "days": 1}]
    )
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
