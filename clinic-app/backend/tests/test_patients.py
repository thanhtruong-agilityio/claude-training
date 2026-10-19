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
    names = [p["full_name"] for p in client.post("/patients/search", json={"q": "nguyễn"}).json()]
    assert names == ["Nguyễn Văn A"]


def test_search_by_phone(client):
    client.post("/patients", json={"full_name": "A", "phone": "0900000001"})
    client.post("/patients", json={"full_name": "B", "phone": "0911111111"})
    names = [p["full_name"] for p in client.post("/patients/search", json={"q": "0911"}).json()]
    assert names == ["B"]


def test_search_respects_include_archived(client, patient):
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    assert client.post("/patients/search", json={"q": "test"}).json() == []
    shown = client.post("/patients/search", json={"q": "test", "include_archived": True}).json()
    assert [p["id"] for p in shown] == [patient["id"]]


def test_get_list_ignores_q(client):
    client.post("/patients", json={"full_name": "A"})
    client.post("/patients", json={"full_name": "B"})
    names = [p["full_name"] for p in client.get("/patients", params={"q": "A"}).json()]
    assert names == ["A", "B"]


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
