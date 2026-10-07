#!/usr/bin/env python3
"""Print genuine, current session 9–12 observations without changing lab objects.

This is a live observer, not a replay of the earlier mutating lab transcripts.
Only session 12 opens a temporary loopback port-forward, which is stopped on exit.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import selectors
import shlex
import subprocess
import time
from urllib.parse import urlparse


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("session", choices=("9", "10", "11", "12"))
parser.add_argument("--kubeconfig", type=Path, required=True)
parser.add_argument("--context", choices=("devops-oct7",), required=True)
parser.add_argument("--view", choices=("resources", "dns"), default="resources")
args = parser.parse_args()
if args.view == "dns" and args.session != "11":
    parser.error("The DNS view belongs to session 11")
if not args.kubeconfig.is_file():
    parser.error("The explicitly supplied isolated kubeconfig must exist")

environment = os.environ.copy()
environment["KUBECONFIG"] = str(args.kubeconfig.resolve())
base = ["kubectl", "--context", args.context, "--request-timeout=10s"]
namespace = "devops-homework"
server = subprocess.check_output(
    base + ["config", "view", "--minify", "-o", "jsonpath={.clusters[0].cluster.server}"],
    env=environment, text=True, timeout=15,
).strip()
if urlparse(server).scheme != "https" or urlparse(server).hostname not in ("127.0.0.1", "localhost", "::1"):
    parser.error("Refusing a Kubernetes API that is not on loopback")

print(f"LIVE session {args.session} ({args.view}) | {datetime.now(timezone.utc).isoformat()}", flush=True)
print(f"KUBECONFIG={environment['KUBECONFIG']}", flush=True)
print(f"Context={args.context}; namespace={namespace}; API={server}", flush=True)
print("Current observations only. Earlier rollout/failure transitions remain in the timestamped lab logs.", flush=True)


def run(command, timeout=20):
    print("\n$ " + shlex.join(command), flush=True)
    result = subprocess.run(command, env=environment, text=True, capture_output=True, timeout=timeout)
    if result.stdout:
        print(result.stdout.rstrip(), flush=True)
    if result.stderr:
        print(result.stderr.rstrip(), flush=True)
    if result.returncode:
        raise SystemExit(f"LIVE CHECK FAILED: exit {result.returncode}; output retained above")
    return result.stdout


def k(*words):
    return run(base + ["-n", namespace] + list(words))


def http_from_client(url):
    return k("exec", "dns-client", "--", "wget", "-T", "5", "-qO-", url)


if args.session == "9":
    run(base + ["get", "nodes", "-o", "wide"])
    run(base + ["-n", "kube-system", "get", "pods"])
    k("get", "serviceaccount", "default")
    k("get", "pod", "dns-client", "-o", "wide")
elif args.session == "10":
    k("get", "deployment", "core-web", "web-blue", "web-green", "web-stable", "web-canary", "recreate-web")
    k("get", "replicaset/replica-web", "daemonset/node-agent", "pod/standalone-web")
    k("rollout", "history", "deployment/core-web")
    k("get", "endpointslices", "-l", "kubernetes.io/service-name=blue-green", "-o", "wide")
    assert "v1" in http_from_client("http://core-web"), "Current core-web response is not the expected restored v1"
    assert "green" in http_from_client("http://blue-green"), "Current blue/green route is not green"
elif args.session == "11" and args.view == "dns":
    for name in (
        "web-clusterip.devops-homework.svc.cluster.local.",
        "external-docs.devops-homework.svc.cluster.local.",
        "web-headless.devops-homework.svc.cluster.local.",
        "stateful-web-0.web-headless.devops-homework.svc.cluster.local.",
    ):
        k("exec", "dns-client", "--", "nslookup", name)
elif args.session == "11":
    k("get", "service", "web-clusterip", "web-nodeport", "web-loadbalancer", "external-docs", "web-headless")
    k("get", "statefulset/stateful-web", "pod/stateful-web-0", "pod/stateful-web-1")
    k("get", "endpointslices", "-l", "kubernetes.io/service-name=web-clusterip", "-o", "wide")
    assert "v1" in http_from_client("http://web-clusterip"), "ClusterIP did not serve v1"
    node = run(base + ["get", "node", "-o", 'jsonpath={.items[0].status.addresses[?(@.type=="InternalIP")].address}']).strip()
    assert "v1" in http_from_client(f"http://{node}:30081"), "NodePort did not serve v1"
    assert "v1" in http_from_client("http://web-loadbalancer"), "LoadBalancer internal route did not serve v1"
    print("LoadBalancer above is tested internally only; <pending> is not external/tunnel verification.", flush=True)
elif args.session == "12":
    k("get", "deployment/demo-frontend", "deployment/demo-backend", "configmap/demo-config", "secret/demo-credentials", "ingress/demo-ingress")
    k("exec", "deployment/demo-backend", "--", "python3", "-c",
      'import os; print("environment="+os.environ["ENVIRONMENT"]); print("secret_loaded="+str(bool(os.environ.get("DEMO_TOKEN"))))')
    command = base + ["-n", "ingress-nginx", "port-forward", "--address=127.0.0.1", "service/ingress-nginx-controller", ":80"]
    print("\n$ " + shlex.join(command), flush=True)
    # kubectl selects an available local port; never reuse or stop another forward.
    forward = subprocess.Popen(command, env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        deadline = time.monotonic() + 15
        local_port = None
        with selectors.DefaultSelector() as selector:
            selector.register(forward.stdout, selectors.EVENT_READ)
            while time.monotonic() < deadline:
                if selector.select(timeout=1):
                    line = forward.stdout.readline()
                    if not line:
                        break
                    print(line.rstrip(), flush=True)
                    match = re.search(r"Forwarding from 127\.0\.0\.1:(\d+) ->", line)
                    if match:
                        local_port = match.group(1)
                        break
                if forward.poll() is not None:
                    break
        if local_port is None:
            raise RuntimeError("Own temporary ingress port-forward did not become ready")
        curl = ["curl", "--noproxy", "*", "--fail", "--silent", "--show-error", "--max-time", "5", "-H", "Host: devops.test"]
        frontend = run(curl + [f"http://127.0.0.1:{local_port}/"])
        assert "DevOps session 12 frontend" in frontend
        backend = json.loads(run(curl + [f"http://127.0.0.1:{local_port}/api/health"]))
        assert backend["secret_loaded"] is True
        assert backend["service"] == "DevOps session 12 API"
    finally:
        forward.terminate()
        forward.wait(timeout=10)
        print("Stopped only this observer's temporary ingress port-forward.", flush=True)

print(f"\nLIVE session {args.session} ({args.view}) OBSERVATIONS COMPLETE; no lab objects changed.", flush=True)
