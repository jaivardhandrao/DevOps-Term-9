"""Exercise a running loopback demo through Nginx. Creates and deletes one task."""
import json
import os
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

base = os.getenv("TASKBOARD_URL", "http://127.0.0.1:18080")
if urlparse(base).hostname not in {"localhost", "127.0.0.1", "::1"}:
    raise SystemExit("Smoke mutations are restricted to an explicitly local demo.")


def request(path, method="GET", body=None, expected=200):
    req = Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                  method=method, headers={"Content-Type": "application/json"})
    try:
        response = urlopen(req, timeout=10)
    except HTTPError as exception:
        response = exception
    with response:
        data = response.read().decode()
        assert response.status == expected, (method, path, response.status, data)
        print(f"PASS {method} {path}: {response.status}")
        return json.loads(data) if data and response.headers.get("content-type", "").startswith("application/json") else data


if __name__ == "__main__":
    assert 'TaskBoard' in request('/')
    assert request('/health')["status"] == "alive"
    assert request('/ready')["status"] == "ready"
    original = request('/api/tasks/stats')
    task = request('/api/tasks', 'POST', {"title": "Disposable smoke check", "priority": "high"}, 201)
    path = f"/api/tasks/{task['id']}"
    try:
        assert request(path)["title"] == "Disposable smoke check"
        assert any(item["id"] == task["id"] for item in request('/api/tasks?status=todo'))
        assert request(path, 'PUT', {"title": "Disposable smoke check", "status": "done"})["status"] == "done"
        assert request('/api/tasks/stats')["done"] == original["done"] + 1
        request('/api/tasks', 'POST', {"title": " "}, 422)
        assert 'taskboard_http_requests_total' in request('/metrics')
    finally:
        request(path, 'DELETE', expected=204)
    request(path, expected=404)
    assert request('/api/tasks/stats') == original
    print("PASS full CRUD, validation, aggregate counts, health, readiness and Prometheus metrics through Nginx/PostgreSQL")
