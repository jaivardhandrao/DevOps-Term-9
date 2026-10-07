#!/usr/bin/env python3
"""Capture genuine local sessions 9–12 evidence; never uses the current context implicitly."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
NS = "devops-homework"
parser = argparse.ArgumentParser()
parser.add_argument("--context", required=True)
parser.add_argument("--session", choices=["9", "10", "11", "12"], required=True)
args = parser.parse_args()
if not args.context.startswith("devops-"):
    parser.error("Use an explicitly named disposable devops- local context")
os.chdir(ROOT)
base = ["kubectl", "--context", args.context]
server = subprocess.check_output(base + ["config", "view", "--minify", "-o", "jsonpath={.clusters[0].cluster.server}"], text=True)
if not server.startswith(("https://127.0.0.1:", "https://localhost:")):
    parser.error("Refusing a non-loopback Kubernetes API")
out = ROOT / "evidence" / "october-7" / ("session-" + args.session)
out.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
log = (out / (stamp + ".txt")).open("x")


def record(text):
    print(text, flush=True)
    log.write(text + "\n")
    log.flush()


def run(command, *, check=True, stdin=None, timeout=240):
    record("\n$ " + shlex.join(command))
    result = subprocess.run(command, input=stdin, capture_output=True, text=True, timeout=timeout)
    record(result.stdout.rstrip())
    if result.stderr:
        record(result.stderr.rstrip())
    record("exit=" + str(result.returncode))
    if check and result.returncode:
        raise RuntimeError("Command failed; retained exact output above")
    return result.stdout


def k(*words, **kw):
    return run(base + ["-n", NS] + list(words), **kw)


def apply(*files):
    words = []
    for file in files:
        words += ["-f", file]
    return k("apply", *words)


def wait(resource):
    return k("rollout", "status", resource, "--timeout=240s")


def request(url, expected):
    for attempt in range(30):
        text = k("exec", "dns-client", "--", "wget", "-T", "4", "-qO-", url, check=False)
        if expected in text:
            return text
        time.sleep(2)
    raise AssertionError("Expected response was not observed: " + expected)


def until(arguments, predicate, limit=120):
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        result = k(*arguments, check=False)
        if predicate(result):
            return result
        time.sleep(3)
    raise AssertionError("Expected state was not observed")


record("Agent-executed isolated coursework lab, not a student-run claim.")
record("UTC: " + datetime.now(timezone.utc).isoformat())
record("Session: " + args.session + "; context: " + args.context)
try:
    if args.session == "9":
        run(base + ["wait", "--for=condition=Ready", "nodes", "--all", "--timeout=300s"])
        run(base + ["-n", "kube-system", "rollout", "status", "deployment/coredns", "--timeout=180s"])
        run(base + ["cluster-info"])
        run(base + ["get", "nodes", "-o", "wide"])
        apply("kubernetes-fundamentals/namespace.yaml")
        k("wait", "--for=create", "serviceaccount/default", "--timeout=180s")
        apply("kubernetes-services/client.yaml")
        k("wait", "--for=condition=Ready", "pod/dns-client", "--timeout=240s")
        run(base + ["-n", "kube-system", "get", "pods", "-o", "wide"])
    elif args.session == "10":
        folder = "kubernetes-core-objects/"
        apply(*(folder + f for f in ["pod.yaml", "replicaset.yaml", "deployment-v1.yaml", "service.yaml", "daemonset.yaml"]))
        wait("deployment/core-web")
        k("wait", "--for=condition=Ready", "pod/standalone-web", "--timeout=180s")
        k("get", "pods", "-l", "app=replica-web", "-o", "wide")
        k("scale", "replicaset/replica-web", "--replicas=3")
        k("delete", "pods", "-l", "app=replica-web")
        k("wait", "--for=jsonpath={.status.readyReplicas}=3", "replicaset/replica-web", "--timeout=180s")
        k("get", "pods", "-l", "app=replica-web", "-o", "wide")
        request("http://core-web", "v1")
        apply(folder + "deployment-v2.yaml")
        k("get", "pods", "-l", "app=core-web", "--show-labels")
        wait("deployment/core-web")
        request("http://core-web", "v2")
        k("rollout", "undo", "deployment/core-web")
        wait("deployment/core-web")
        request("http://core-web", "v1")
        k("rollout", "history", "deployment/core-web")
        apply(folder + "strategies/blue-green.yaml")
        wait("deployment/web-blue")
        wait("deployment/web-green")
        request("http://blue-green", "blue")
        k("get", "endpointslices", "-l", "kubernetes.io/service-name=blue-green", "-o", "wide")
        k("patch", "service", "blue-green", "--type=merge", "-p", '{"spec":{"selector":{"app":"blue-green","slot":"green"}}}')
        request("http://blue-green", "green")
        k("get", "endpointslices", "-l", "kubernetes.io/service-name=blue-green", "-o", "wide")
        apply(folder + "strategies/canary.yaml")
        wait("deployment/web-stable")
        wait("deployment/web-canary")
        k("get", "endpointslices", "-l", "kubernetes.io/service-name=canary-web", "-o", "wide")
        observations = k("exec", "dns-client", "--", "sh", "-c", "for i in $(seq 1 40); do wget -T 3 -qO- http://canary-web; done")
        assert "stable" in observations and "canary" in observations
        record("Observed stable/canary responses: " + str(observations.count("stable")) + "/" + str(observations.count("canary")) + "; random connection distribution, not a guaranteed traffic weight.")
        apply(folder + "strategies/recreate-v1.yaml")
        wait("deployment/recreate-web")
        old = json.loads(k("get", "pods", "-l", "app=recreate-web", "-o", "json"))["items"]
        old_names = [p["metadata"]["name"] for p in old]
        apply(folder + "strategies/recreate-v2.yaml")
        k("get", "pods", "-l", "app=recreate-web", "--show-labels")
        wait("deployment/recreate-web")
        k("get", "events", "--field-selector", "involvedObject.name=recreate-web", "--sort-by=.metadata.creationTimestamp")
        current = json.loads(k("get", "pods", "-l", "app=recreate-web", "-o", "json"))["items"]
        assert all(p["metadata"]["name"] not in old_names for p in current)
        assert all(p["metadata"]["labels"]["version"] == "v2" for p in current)
        for file in sorted((ROOT / folder / "lifecycle").glob("*.yaml")):
            apply(str(file.relative_to(ROOT)))
        k("wait", "--for=jsonpath={.status.phase}=Succeeded", "pod/lifecycle-succeeded", "--timeout=120s")
        k("wait", "--for=jsonpath={.status.phase}=Failed", "pod/lifecycle-failed", "--timeout=120s")
        k("wait", "--for=condition=Ready", "pod/lifecycle-running", "pod/lifecycle-init", "pod/lifecycle-multi", "pod/lifecycle-termination", "--timeout=180s")
        until(["get", "pod", "lifecycle-crashloop", "-o", "json"], lambda s: "CrashLoopBackOff" in s)
        until(["get", "pod", "lifecycle-image-error", "-o", "json"], lambda s: "ImagePullBackOff" in s or "ErrImagePull" in s)
        k("get", "pod", "lifecycle-readiness", "-o", "wide")
        k("exec", "lifecycle-readiness", "--", "touch", "/tmp/ready")
        k("wait", "--for=condition=Ready", "pod/lifecycle-readiness", "--timeout=60s")
        until(["get", "pod", "lifecycle-liveness", "-o", "jsonpath={.status.containerStatuses[0].restartCount}"], lambda s: s.strip().isdigit() and int(s.strip()) > 0, limit=120)
        k("wait", "--for=condition=Ready", "pod/lifecycle-startup", "--timeout=100s")
        for pod in ["running", "pending", "succeeded", "failed", "crashloop", "image-error", "readiness", "liveness", "startup", "init", "multi", "termination"]:
            k("describe", "pod", "lifecycle-" + pod)
        k("logs", "lifecycle-init", "-c", "app")
        k("logs", "lifecycle-multi", "-c", "sidecar")
        # Follow the exact test Pod before deleting it to capture its SIGTERM handler.
        follow = subprocess.Popen(base + ["-n", NS, "logs", "-f", "lifecycle-termination"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        time.sleep(1)
        k("delete", "pod", "lifecycle-termination", "--wait=true")
        termination, _ = follow.communicate(timeout=30)
        record("$ kubectl logs -f lifecycle-termination (during deletion)\n" + termination)
        assert "cleanup-complete" in termination
    elif args.session == "11":
        folder = "kubernetes-services/"
        apply(*(folder + f for f in ["deployment.yaml", "clusterip.yaml", "nodeport.yaml", "externalname.yaml", "headless.yaml", "optional/loadbalancer.yaml"]))
        wait("deployment/service-web")
        wait("statefulset/stateful-web")
        k("get", "services", "-o", "wide")
        # BusyBox can return 1 after resolving a short name if later search-list
        # candidates fail. Keep that actual output, then assert absolute queries.
        short = k("exec", "dns-client", "--", "nslookup", "web-clusterip", check=False)
        assert "web-clusterip.devops-homework.svc.cluster.local" in short
        for name in ["web-clusterip.devops-homework.svc.cluster.local.", "external-docs.devops-homework.svc.cluster.local.", "web-headless.devops-homework.svc.cluster.local.", "stateful-web-0.web-headless.devops-homework.svc.cluster.local."]:
            k("exec", "dns-client", "--", "nslookup", name)
        request("http://web-clusterip", "v1")
        node = run(base + ["get", "node", "-o", 'jsonpath={.items[0].status.addresses[?(@.type=="InternalIP")].address}']).strip()
        request("http://" + node + ":30081", "v1")
        request("http://web-loadbalancer", "v1")
        k("exec", "dns-client", "--", "cat", "/etc/resolv.conf")
        k("patch", "service", "web-clusterip", "--type=merge", "-p", '{"spec":{"selector":{"app":"deliberately-missing"}}}')
        time.sleep(3)
        k("get", "endpointslices", "-l", "kubernetes.io/service-name=web-clusterip", "-o", "yaml")
        k("exec", "dns-client", "--", "wget", "-T", "3", "-qO-", "http://web-clusterip", check=False)
        apply(folder + "clusterip.yaml")
        request("http://web-clusterip", "v1")
        k("get", "endpointslices", "-l", "kubernetes.io/service-name=web-clusterip", "-o", "wide")
        record("LoadBalancer Service internal traffic checked above; an assigned external address/tunnel needs separate evidence.")
    elif args.session == "12":
        folder = "kubernetes-ingress-configmaps-secrets/"
        apply(folder + "configmap.yaml", folder + "backend-code.yaml")
        with tempfile.TemporaryDirectory(prefix="devops-secret-") as temp:
            file = Path(temp) / "secret.env"
            file.write_text("DEMO_TOKEN=" + secrets.token_hex(24) + "\n")
            file.chmod(0o600)
            existing = k("get", "secret", "demo-credentials", "--ignore-not-found", "-o", "name").strip()
            if not existing:
                k("create", "secret", "generic", "demo-credentials", "--from-env-file=" + str(file))
        apply(folder + "frontend.yaml", folder + "backend.yaml")
        # A rerun may have changed the ConfigMap back from the previous staging drill.
        # Environment injection happens at container start, so start fresh processes.
        k("rollout", "restart", "deployment/demo-backend")
        wait("deployment/demo-frontend")
        wait("deployment/demo-backend")
        k("exec", "deployment/demo-backend", "--", "python3", "-c", 'import os; print("environment="+os.environ["ENVIRONMENT"]); print("secret_loaded="+str(bool(os.environ.get("DEMO_TOKEN"))))')
        # Reproduce the instructor's newline bug with public fixture bytes, not a credential.
        run(["python3", "-c", "import base64; x=b'classroom-demo'; bad=base64.b64encode(x+b'\\n'); good=base64.b64encode(x); print('before decoded match:',base64.b64decode(bad)==x); print('after decoded match:',base64.b64decode(good)==x); assert base64.b64decode(bad)!=x and base64.b64decode(good)==x"])
        apply(folder + "ingress.yaml")
        # The ingress controller is installed separately by the lab operator, never on a remote cluster.
        forward = subprocess.Popen(base + ["-n", "ingress-nginx", "port-forward", "--address=127.0.0.1", "service/ingress-nginx-controller", "18084:80"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            time.sleep(3)
            curl = ["curl", "--fail", "--silent", "--show-error", "--retry", "15", "--retry-all-errors", "--retry-delay", "1", "--max-time", "5", "-H", "Host: devops.test"]
            run(curl + ["http://127.0.0.1:18084/"])
            response = run(curl + ["http://127.0.0.1:18084/api/health"])
            assert json.loads(response)["secret_loaded"] is True
            k("patch", "configmap", "demo-config", "--type=merge", "-p", '{"data":{"ENVIRONMENT":"staging"}}')
            before = k("exec", "deployment/demo-backend", "--", "python3", "-c", 'import os; print(os.environ["ENVIRONMENT"])')
            record("Existing process keeps its original environment: " + before.strip())
            k("rollout", "restart", "deployment/demo-backend")
            wait("deployment/demo-backend")
            for attempt in range(30):
                response = run(curl + ["http://127.0.0.1:18084/api/health"])
                if json.loads(response)["environment"] == "staging":
                    break
                time.sleep(1)
            else:
                raise AssertionError("Ingress never observed the restarted staging configuration")
            # Deliberate routing failure and repair, confined to this exercise's Ingress.
            k("patch", "ingress", "demo-ingress", "--type=json", "-p", '[{"op":"replace","path":"/spec/rules/0/http/paths/0/backend/service/name","value":"deliberately-missing"}]')
            k("describe", "ingress", "demo-ingress")
            for attempt in range(30):
                status = run(["curl", "--silent", "--show-error", "--max-time", "5", "-o", "/dev/null", "-w", "%{http_code}\\n", "-H", "Host: devops.test", "http://127.0.0.1:18084/api/health"]).strip()
                if status in {"502", "503"}:
                    break
                time.sleep(1)
            else:
                raise AssertionError("Deliberate broken route never produced an upstream failure")
            apply(folder + "ingress.yaml")
            response = run(curl + ["http://127.0.0.1:18084/api/health"])
            assert json.loads(response)["secret_loaded"] is True
            k("get", "configmaps,ingress,services")
        finally:
            forward.terminate()
            forward.wait(timeout=15)
    record("\nSESSION CHECKS PASSED at " + datetime.now(timezone.utc).isoformat())
finally:
    log.close()
