def test_create_and_list(client):
    res = client.post("/todos", json={"title": "buy milk"})
    assert res.status_code == 201
    assert res.json()["done"] is False

    todos = client.get("/todos").json()
    assert [t["title"] for t in todos] == ["buy milk"]


def test_create_rejects_empty_title(client):
    assert client.post("/todos", json={"title": ""}).status_code == 422


def test_mark_done(client):
    todo_id = client.post("/todos", json={"title": "a"}).json()["id"]
    res = client.patch(f"/todos/{todo_id}", json={"done": True})
    assert res.json()["done"] is True


def test_update_missing_returns_404(client):
    assert client.patch("/todos/999", json={"done": True}).status_code == 404


def test_delete_removes_todo(client):
    todo_id = client.post("/todos", json={"title": "a"}).json()["id"]
    client.delete(f"/todos/{todo_id}")
    assert client.get("/todos").json() == []


def test_delete_missing_returns_404(client):
    assert client.delete("/todos/999").status_code == 404


def test_create_rejects_whitespace_only_title(client):
    assert client.post("/todos", json={"title": "   "}).status_code == 422


def test_update_rejects_whitespace_only_title(client):
    todo_id = client.post("/todos", json={"title": "a"}).json()["id"]
    res = client.patch(f"/todos/{todo_id}", json={"title": "   "})
    assert res.status_code == 422


def test_create_trims_title(client):
    res = client.post("/todos", json={"title": " a "})
    assert res.json()["title"] == "a"


def test_update_trims_title(client):
    todo_id = client.post("/todos", json={"title": "a"}).json()["id"]
    res = client.patch(f"/todos/{todo_id}", json={"title": " b "})
    assert res.json()["title"] == "b"
