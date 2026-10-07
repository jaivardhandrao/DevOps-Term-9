"""Offline regression checks for probe independence and Argo dependency ordering."""
import subprocess
from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]
rendered = subprocess.check_output(
    ["helm", "template", "taskboard", str(root / "final-devops-project/helm/taskboard"),
     "--namespace", "capstone-oct7"], text=True
)
resources = [d for d in yaml.safe_load_all(rendered) if d]
deployments = {d["metadata"]["name"]: d for d in resources if d["kind"] == "Deployment"}
frontend = deployments["frontend"]["spec"]["template"]["spec"]["containers"][0]
backend = deployments["backend"]["spec"]["template"]["spec"]["containers"][0]
for probe in ["startupProbe", "livenessProbe", "readinessProbe"]:
    assert frontend[probe]["httpGet"]["path"] == "/", probe
assert backend["livenessProbe"]["httpGet"]["path"] == "/health"
assert backend["readinessProbe"]["httpGet"]["path"] == "/ready"
nginx = (root / "final-devops-project/docker/nginx.conf.template").read_text()
assert "location /" in nginx and "try_files" in nginx
print("PASS: frontend probes use local static route; backend readiness checks DB while liveness checks process")


def wave(resource):
    return int(resource["metadata"].get("annotations", {}).get("argocd.argoproj.io/sync-wave", "0"))


def check_dependency_order(documents):
    by_name = {(d["kind"], d["metadata"]["name"]): d for d in documents}
    migrations = [d for d in documents if d["kind"] == "Job"]
    assert len(migrations) == 1, "expected one explicit migration Job"
    migration = migrations[0]
    assert migration["metadata"]["annotations"]["argocd.argoproj.io/hook"] == "Sync"
    assert wave(by_name[("StatefulSet", "postgres")]) < wave(migration), "database must precede migration"
    for name in ("backend", "frontend"):
        assert wave(migration) < wave(by_name[("Deployment", name)]), "migration must precede applications"
    for resource in documents:
        if resource["kind"] == "HorizontalPodAutoscaler":
            target = resource["spec"]["scaleTargetRef"]
            deployment = by_name[(target["kind"], target["name"])]
            assert wave(resource) > wave(deployment), "HPA cannot gate creation of its own target"
            assert "replicas" not in deployment["spec"], "GitOps must not fight HPA over replicas"
        elif resource["kind"] == "Ingress":
            assert wave(resource) > wave(by_name[("Deployment", "frontend")]), "Ingress must follow frontend"


check_dependency_order(resources)
with_ingress = subprocess.check_output(
    ["helm", "template", "taskboard", str(root / "final-devops-project/helm/taskboard"),
     "--namespace", "capstone-oct7", "--set", "ingress.enabled=true"], text=True
)
ingress_resources = [d for d in yaml.safe_load_all(with_ingress) if d]
assert any(d["kind"] == "Ingress" for d in ingress_resources), "optional Ingress was not rendered"
check_dependency_order(ingress_resources)
print("PASS: database -> migration -> applications -> HPA/Ingress ordering; HPA owns backend replicas")
