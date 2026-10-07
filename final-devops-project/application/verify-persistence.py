"""Disrupt only this explicitly named disposable Compose demo, then recover it."""
import os
from pathlib import Path
import subprocess
import time
from urllib.error import URLError

from smoke import request

project = Path(__file__).resolve().parent.parent
if os.getenv("TASKBOARD_URL") or os.getenv("COMPOSE_FILE") or os.getenv("DOCKER_HOST"):
    raise SystemExit("Use the default local Docker context and this project's loopback URL.")


def compose(*args):
    subprocess.run(["docker", "compose", "-f", str(project / "compose.yaml"), "-p", "devops-oct7-capstone", *args],
                   cwd=project, check=True)


if __name__ == "__main__":
    task = request('/api/tasks', 'POST', {"title": "Disposable persistence probe", "status": "in_progress"}, 201)
    path = f"/api/tasks/{task['id']}"
    try:
        compose("stop", "postgres")
        assert request('/health')["status"] == "alive"
        request('/ready', expected=503)
        print("PASS stopped database causes readiness 503 while liveness remains 200")
    finally:
        compose("start", "postgres")
    compose("restart", "backend")
    for attempt in range(60):
        try:
            request('/ready')
            break
        except (URLError, AssertionError):
            time.sleep(0.5)
    else:
        raise RuntimeError("Readiness did not recover; test task retained for inspection")
    retained = request(path)
    assert retained["title"] == task["title"] and retained["status"] == "in_progress"
    print("PASS task survives PostgreSQL stop/start and backend restart")
    request(path, "DELETE", expected=204)
    print("PASS disposable persistence probe removed; other tasks retained")
