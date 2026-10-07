import pytest
from sqlalchemy.exc import OperationalError
from app.database import get_db
from app.main import app


def test_crud_persists_and_deletes(client):
    payload = {"title": "  Verify deployment  ", "description": "Check rollout", "priority": "high"}
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Verify deployment"
    assert response.headers["location"] == f"/api/tasks/{task['id']}"
    assert client.get(response.headers["location"]).json()["description"] == "Check rollout"
    changed = client.put(response.headers["location"], json={**payload, "status": "done"})
    assert changed.status_code == 200
    assert changed.json()["status"] == "done"
    assert client.get("/api/tasks/stats").json() == {"total": 1, "todo": 0, "in_progress": 0, "done": 1}
    assert client.delete(response.headers["location"]).status_code == 204
    assert client.get(response.headers["location"]).status_code == 404
    assert client.get("/api/tasks").json() == []


@pytest.mark.parametrize("payload", [{"title": " "}, {"title": "x" * 161}, {"title": "x", "status": "invalid"},
    {"title": "x", "priority": "urgent"}, {"title": "x", "description": "x" * 5001}, {"title": "x", "id": 5}])
def test_invalid_input_rejected(client, payload):
    assert client.post("/api/tasks", json=payload).status_code == 422
    assert client.get("/api/tasks").json() == []


def test_filters_pagination_and_stats(client):
    for title, status in [("One", "todo"), ("Two", "done"), ("Three", "done")]:
        assert client.post("/api/tasks", json={"title": title, "status": status}).status_code == 201
    assert [task["title"] for task in client.get("/api/tasks?status=done&limit=1&offset=1").json()] == ["Two"]
    assert client.get("/api/tasks/stats").json() == {"total": 3, "todo": 1, "in_progress": 0, "done": 2}
    for query in ("limit=0", "limit=501", "offset=-1", "status=unknown"):
        assert client.get(f"/api/tasks?{query}").status_code == 422


def test_missing_task_cannot_be_updated_or_deleted(client):
    assert client.put("/api/tasks/987", json={"title": "Missing"}).status_code == 404
    assert client.delete("/api/tasks/987").status_code == 404


def test_liveness_readiness_and_low_cardinality_metrics(client):
    assert client.get("/health").json() == {"status": "alive"}
    assert client.get("/ready").json() == {"status": "ready"}
    client.get("/api/tasks/2345")
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert 'path="/api/tasks/{task_id}"' in metrics.text
    assert 'path="/api/tasks/2345"' not in metrics.text


def test_database_outage_keeps_liveness_but_fails_readiness(client):
    class BrokenDB:
        def execute(self, *args):
            raise OperationalError("query", {}, Exception("private database details"))
    app.dependency_overrides[get_db] = lambda: BrokenDB()
    assert client.get("/health").status_code == 200
    response = client.get("/ready")
    assert response.status_code == 503
    assert "private" not in response.text
