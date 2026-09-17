#!/usr/bin/env bash
# Student-run lab: creates a disposable local cluster and takes interactive macOS screenshots.
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_dir"
for tool in docker kubectl minikube python3 screencapture; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'Missing prerequisite: %s\n' "$tool" >&2
    printf 'On macOS, install the missing CLI first. Minikube: brew install minikube\n' >&2
    exit 1
  fi
done
if [[ -n "${DOCKER_HOST:-}" ]] || [[ "$(docker context inspect --format '{{.Endpoints.docker.Host}}')" != unix://* ]]; then
  printf 'Select a local Docker Desktop Unix-socket context first. Remote Docker is not supported.\n' >&2
  exit 1
fi

profile="devops-evidence-$(date +%Y%m%d-%H%M%S)"
output_dir="$repo_dir/evidence/live/$profile"
mkdir -p "$output_dir"
scratch_dir="$(mktemp -d -t devops-evidence)"
forward_pid=""
trap 'if [[ -n "$forward_pid" ]]; then kill "$forward_pid" 2>/dev/null || true; fi; rm -rf "$scratch_dir"' EXIT
exec > >(tee "$output_dir/run.txt") 2>&1

run() {
  printf '\n$'
  printf ' %q' "$@"
  printf '\n'
  "$@"
}
k() { run kubectl "--context=$profile" -n devops-homework "$@"; }
capture() {
  printf '\nJaivardhan D. Rao | 24BCS10117 | %s\n' "$2"
  printf 'Click this Terminal window in the screenshot picker. Cancel stops the run.\n'
  screencapture -i -w -o "$output_dir/$1.png"
  test -s "$output_dir/$1.png"
}

printf 'Student-run local Kubernetes lab. Profile: %s\n' "$profile"
printf 'This creates Kubernetes control-plane state and deploys the coursework examples.\n'
run minikube start -p "$profile" --driver=docker
run kubectl "--context=$profile" cluster-info
run kubectl "--context=$profile" get nodes -o wide
run kubectl "--context=$profile" apply -f kubernetes-fundamentals/namespace.yaml
k apply -f kubernetes-services/client.yaml
k wait --for=condition=Ready pod/dns-client --timeout=180s
capture 01-fundamentals 'Kubernetes Fundamentals: actual local cluster'

k apply -f kubernetes-core-objects/pod.yaml -f kubernetes-core-objects/replicaset.yaml -f kubernetes-core-objects/deployment-v1.yaml -f kubernetes-core-objects/service.yaml
k wait --for=condition=Ready pod/standalone-web --timeout=180s
k rollout status deployment/core-web --timeout=180s
k scale replicaset/replica-web --replicas=3
k delete pods -l app=replica-web
k wait --for=jsonpath='{.status.readyReplicas}'=3 replicaset/replica-web --timeout=180s
k exec dns-client -- wget -qO- http://core-web
k apply -f kubernetes-core-objects/deployment-v2.yaml
k rollout status deployment/core-web --timeout=180s
k exec dns-client -- wget -qO- http://core-web
k rollout undo deployment/core-web
k rollout status deployment/core-web --timeout=180s
k exec dns-client -- wget -qO- http://core-web
k rollout history deployment/core-web
k get pods,replicasets,deployments -o wide
capture 02-session-10 'Session 10: replicas, rollout, rollback and HTTP'

k apply -f kubernetes-services/deployment.yaml -f kubernetes-services/clusterip.yaml -f kubernetes-services/nodeport.yaml -f kubernetes-services/externalname.yaml -f kubernetes-services/headless.yaml
k rollout status deployment/service-web --timeout=180s
k rollout status statefulset/stateful-web --timeout=180s
k exec dns-client -- nslookup web-clusterip.devops-homework.svc.cluster.local
k exec dns-client -- wget -qO- http://web-clusterip
k exec dns-client -- nslookup external-docs
k exec dns-client -- nslookup stateful-web-0.web-headless.devops-homework.svc.cluster.local
node_ip="$(kubectl "--context=$profile" get node -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')"
k exec dns-client -- wget -qO- "http://$node_ip:30081"
k get services
k get endpointslices -l kubernetes.io/service-name=web-clusterip -o wide
capture 03-session-11 'Session 11: DNS, ClusterIP, NodePort and headless discovery'

python3 - "$scratch_dir/secret.env" <<'PY'
import os
import secrets
import sys
with open(sys.argv[1], 'x') as secret_file:
    os.chmod(sys.argv[1], 0o600)
    secret_file.write('DEMO_TOKEN=' + secrets.token_hex(16) + '\n')
PY
k apply -f kubernetes-ingress-configmaps-secrets/configmap.yaml -f kubernetes-ingress-configmaps-secrets/backend-code.yaml
k create secret generic demo-credentials "--from-env-file=$scratch_dir/secret.env"
k describe secret demo-credentials
k apply -f kubernetes-ingress-configmaps-secrets/frontend.yaml -f kubernetes-ingress-configmaps-secrets/backend.yaml
k rollout status deployment/demo-frontend --timeout=180s
k rollout status deployment/demo-backend --timeout=180s
run minikube -p "$profile" addons enable ingress
run kubectl "--context=$profile" -n ingress-nginx rollout status deployment/ingress-nginx-controller --timeout=300s
k apply -f kubernetes-ingress-configmaps-secrets/ingress.yaml
kubectl "--context=$profile" -n ingress-nginx port-forward service/ingress-nginx-controller 18084:80 > "$output_dir/port-forward.txt" 2>&1 &
forward_pid=$!
ready=0
for attempt in {1..30}; do
  if curl --fail --silent -H 'Host: devops.test' http://127.0.0.1:18084/api/health > /dev/null; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "$ready" != 1 ]]; then
  printf 'Ingress did not become ready; inspect the captured logs.\n' >&2
  exit 1
fi
run curl --fail --silent --show-error -H 'Host: devops.test' http://127.0.0.1:18084/
run curl --fail --silent --show-error -H 'Host: devops.test' http://127.0.0.1:18084/api/health
k patch configmap demo-config --type=merge -p '{"data":{"ENVIRONMENT":"staging"}}'
k exec deployment/demo-backend -- python3 -c 'import os; print(os.environ["ENVIRONMENT"])'
k rollout restart deployment/demo-backend
k rollout status deployment/demo-backend --timeout=180s
run curl --fail --silent --show-error -H 'Host: devops.test' http://127.0.0.1:18084/api/health
k get configmaps,ingress,services
capture 04-session-12 'Session 12: actual Ingress routes and configuration restart'

printf '\nCaptured actual logs and four Terminal screenshots in:\n%s\n' "$output_dir"
printf 'Additional lifecycle/strategy/TLS exercises remain in the session READMEs.\n'
printf 'The local cluster is retained for those exercises. Cleanup command:\n'
printf 'minikube delete -p %q\n' "$profile"
