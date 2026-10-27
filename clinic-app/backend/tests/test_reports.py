import pytest
import time_machine


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


# --- GET /reports/follow-ups (ticket 14, matrix T14-*) ---------------------

AS_OF = "2026-10-27"
FIELDS = {"patient_id", "full_name", "phone", "follow_up_date", "days_overdue"}


def _due(client, **params):
    return client.get("/reports/follow-ups", params={"as_of": AS_OF, **params})


def _new_patient(client, name, phone=None):
    body = {"full_name": name}
    if phone:
        body["phone"] = phone
    res = client.post("/patients", json=body)
    assert res.status_code == 201, res.text
    return res.json()


def test_t14_01_follow_up_due_today(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-20T09:00:00", follow_up_date="2026-10-27")
    res = _due(client)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["patient_id"] == patient["id"]
    assert body["items"][0]["days_overdue"] == 0
    assert body["items"][0]["follow_up_date"] == "2026-10-27"


def test_t14_02_follow_up_seven_days_overdue(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    items = _due(client).json()["items"]
    assert [(i["patient_id"], i["days_overdue"]) for i in items] == [(patient["id"], 7)]


def test_t14_03_exactly_30_days_overdue_is_listed(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-09-01T09:00:00", follow_up_date="2026-09-27")
    items = _due(client).json()["items"]
    assert [i["days_overdue"] for i in items] == [30]


def test_t14_04_31_days_overdue_is_not_listed(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-09-01T09:00:00", follow_up_date="2026-09-26")
    assert _due(client).json() == {"total": 0, "items": []}


def test_t14_05_follow_up_tomorrow_is_not_listed(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-20T09:00:00", follow_up_date="2026-10-28")
    assert _due(client).json() == {"total": 0, "items": []}


def test_t14_06_patient_came_back_after_follow_up_date(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    make_visit(patient["id"], visited_at="2026-10-22T09:00:00")
    assert _due(client).json() == {"total": 0, "items": []}


def test_t14_07_patient_came_back_on_follow_up_date(client, patient, make_visit):
    # OQ1 working default: same day counts as having come back.
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    make_visit(patient["id"], visited_at="2026-10-20T15:30:00")
    assert _due(client).json() == {"total": 0, "items": []}


def test_t14_08_visit_the_day_before_does_not_count(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    make_visit(patient["id"], visited_at="2026-10-19T23:59:00")
    items = _due(client).json()["items"]
    assert [i["patient_id"] for i in items] == [patient["id"]]


def test_t14_09_soft_deleted_newer_visit_does_not_count(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    newer = make_visit(patient["id"], visited_at="2026-10-22T09:00:00")
    client.delete(f"/visits/{newer['id']}")
    items = _due(client).json()["items"]
    assert [i["patient_id"] for i in items] == [patient["id"]]


def test_t14_10_restored_newer_visit_counts_again(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    newer = make_visit(patient["id"], visited_at="2026-10-22T09:00:00")
    client.delete(f"/visits/{newer['id']}")
    assert client.post(f"/visits/{newer['id']}/restore").status_code == 200
    assert _due(client).json() == {"total": 0, "items": []}


def test_t14_11_carrying_visit_does_not_count_against_itself(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-20T09:00:00", follow_up_date="2026-10-20")
    items = _due(client).json()["items"]
    assert [i["patient_id"] for i in items] == [patient["id"]]


def test_t14_12_soft_deleted_visit_with_follow_up_is_ignored(client, patient, make_visit):
    gone = make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    client.delete(f"/visits/{gone['id']}")
    assert _due(client).json() == {"total": 0, "items": []}


def test_t14_13_archived_patient_is_hidden(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    assert _due(client).json() == {"total": 0, "items": []}


def test_t14_14_unarchived_patient_is_listed_again(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    client.patch(f"/patients/{patient['id']}", json={"is_archived": True})
    client.patch(f"/patients/{patient['id']}", json={"is_archived": False})
    items = _due(client).json()["items"]
    assert [i["patient_id"] for i in items] == [patient["id"]]


def test_t14_15_one_item_per_patient_latest_follow_up_wins(client, patient, make_visit):
    # The later follow-up date is created first, so "last row wins" cannot pass by luck.
    make_visit(patient["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-25")
    make_visit(patient["id"], visited_at="2026-10-05T09:00:00", follow_up_date="2026-10-20")
    body = _due(client).json()
    assert body["total"] == 1
    assert body["items"][0]["follow_up_date"] == "2026-10-25"
    assert body["items"][0]["days_overdue"] == 2


def test_t14_16_two_patients_total_two(client, patient, make_visit):
    other = _new_patient(client, "Second Patient")
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    make_visit(other["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-21")
    body = _due(client).json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_t14_17_order_by_days_overdue_desc(client, make_visit):
    a = _new_patient(client, "A Patient")
    b = _new_patient(client, "B Patient")
    c = _new_patient(client, "C Patient")
    make_visit(a["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-24")  # 3
    make_visit(b["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-17")  # 10
    make_visit(c["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-27")  # 0
    ids = [i["patient_id"] for i in _due(client).json()["items"]]
    assert ids == [b["id"], a["id"], c["id"]]


def test_t14_18_tie_on_days_overdue_sorted_by_name(client, make_visit):
    binh = _new_patient(client, "Binh")
    an = _new_patient(client, "An")
    make_visit(binh["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-22")
    make_visit(an["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-22")
    names = [i["full_name"] for i in _due(client).json()["items"]]
    assert names == ["An", "Binh"]


def test_t14_19_plain_text_comparison_no_accent_or_case_folding(client, make_visit):
    for name in ["Ánh", "Bình", "an"]:
        p = _new_patient(client, name)
        make_visit(p["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-22")
    names = [i["full_name"] for i in _due(client).json()["items"]]
    assert names == ["Bình", "an", "Ánh"]


def test_t14_20_same_name_same_days_sorted_by_patient_id(client, make_visit):
    first = _new_patient(client, "An")
    second = _new_patient(client, "An")
    assert first["id"] < second["id"]
    # create visits in reverse order so insertion order cannot explain the result
    make_visit(second["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-22")
    make_visit(first["id"], visited_at="2026-10-01T09:00:00", follow_up_date="2026-10-22")
    ids = [i["patient_id"] for i in _due(client).json()["items"]]
    assert ids == [first["id"], second["id"]]


def test_t14_21_patient_without_phone_has_null_phone(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    items = _due(client).json()["items"]
    assert len(items) == 1
    assert items[0]["phone"] is None


def test_t14_22_empty_database(client):
    res = _due(client)
    assert res.status_code == 200
    assert res.json() == {"total": 0, "items": []}


def test_t14_23_patients_exist_but_none_due(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00")
    res = _due(client)
    assert res.status_code == 200
    assert res.json() == {"total": 0, "items": []}


@pytest.mark.parametrize(
    "case, value",
    [
        ("t14_24_invalid", "banana"),
        ("t14_25_impossible", "2026-02-30"),
        ("t14_26_wrong_format", "27-10-2026"),
        ("t14_27_empty", ""),
        # date.fromisoformat accepts these on Python 3.11+; only the format check rejects them.
        ("t14_27_compact", "20261027"),
        ("t14_27_iso_week", "2026-W44-2"),
    ],
)
def test_t14_24_to_27_invalid_as_of_is_422(client, case, value):
    res = client.get("/reports/follow-ups", params={"as_of": value})
    assert res.status_code == 422, case


def test_t14_28_default_uses_clinic_date_not_utc_date(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-20T09:00:00", follow_up_date="2026-10-27")
    # 2026-10-27 18:00 UTC is 2026-10-28 01:00 in Asia/Ho_Chi_Minh
    with time_machine.travel("2026-10-27T18:00:00+00:00", tick=False):
        res = client.get("/reports/follow-ups")
    assert res.status_code == 200
    items = res.json()["items"]
    assert [(i["patient_id"], i["days_overdue"]) for i in items] == [(patient["id"], 1)]


def test_t14_29_default_near_midnight_same_date_in_both_zones(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-20T09:00:00", follow_up_date="2026-10-27")
    # 2026-10-27 16:30 UTC is 2026-10-27 23:30 clinic time
    with time_machine.travel("2026-10-27T16:30:00+00:00", tick=False):
        res = client.get("/reports/follow-ups")
    assert res.status_code == 200
    items = res.json()["items"]
    assert [(i["patient_id"], i["days_overdue"]) for i in items] == [(patient["id"], 0)]


def test_t14_30_explicit_as_of_overrides_clock(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    with time_machine.travel("2026-10-27T05:00:00+00:00", tick=False):
        res = client.get("/reports/follow-ups", params={"as_of": "2026-10-20"})
    assert res.status_code == 200
    items = res.json()["items"]
    assert [(i["patient_id"], i["days_overdue"]) for i in items] == [(patient["id"], 0)]


def test_t14_31_old_follow_ups_endpoint_unchanged(client, patient, make_visit):
    visit = make_visit(patient["id"], visited_at="2026-10-20T09:00:00", follow_up_date="2026-10-27")
    make_visit(patient["id"], visited_at="2026-10-20T10:00:00", follow_up_date="2026-10-26")
    rows = client.get("/visits/follow-ups", params={"date": "2026-10-27"}).json()
    assert rows == [
        {
            "visit_id": visit["id"],
            "patient_id": patient["id"],
            "full_name": "Test Patient",
            "phone": None,
            "follow_up_date": "2026-10-27",
        }
    ]


def test_t14_32_response_shape_and_total(client, make_visit):
    for name, phone in [("Shape One", "0900000001"), ("Shape Two", None)]:
        p = _new_patient(client, name, phone)
        make_visit(p["id"], visited_at="2026-10-10T09:00:00", follow_up_date="2026-10-20")
    body = _due(client).json()
    assert set(body) == {"total", "items"}
    assert body["total"] == len(body["items"]) == 2
    for item in body["items"]:
        assert set(item) == FIELDS
    assert body["items"][0]["phone"] == "0900000001"


def test_t14_33_visit_without_follow_up_date_is_ignored(client, patient, make_visit):
    make_visit(patient["id"], visited_at="2026-10-20T09:00:00")
    assert _due(client).json() == {"total": 0, "items": []}
