"""Regression check: losing the backend must not restart a healthy frontend."""
import subprocess
from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]
rendered = subprocess.check_output(
    ["helm", "template", "taskboard", str(root / "final-devops-project/helm/taskboard"),
     "--namespace", "capstone-oct7"], text=True
)
deployments = {d["metadata"]["name"]: d for d in yaml.safe_load_all(rendered)
               if d and d["kind"] == "Deployment"}
frontend = deployments["frontend"]["spec"]["template"]["spec"]["containers"][0]
backend = deployments["backend"]["spec"]["template"]["spec"]["containers"][0]
for probe in ["startupProbe", "livenessProbe", "readinessProbe"]:
    assert frontend[probe]["httpGet"]["path"] == "/", probe
assert backend["livenessProbe"]["httpGet"]["path"] == "/health"
assert backend["readinessProbe"]["httpGet"]["path"] == "/ready"
nginx = (root / "final-devops-project/docker/nginx.conf.template").read_text()
assert "location /" in nginx and "try_files" in nginx
print("PASS: frontend probes use local static route; backend readiness checks DB while liveness checks process")
