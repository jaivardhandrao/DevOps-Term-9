# Kubernetes validation

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117
- **Latest live evidence:** 7 October 2026; September validation retained below as history.
- **Scope:** Kubernetes Fundamentals and sessions 10, 11, and 12.

**October 7 live checks passed for fundamentals, session 10 strategies/lifecycle, session 11
internal Service traffic/DNS, and session 12 HTTP Ingress/configuration/Secret presence.**
The [dated evidence inventory and exact transcripts](evidence/october-7/README.md) record
agent-executed checks on the isolated `devops-oct7` Minikube cluster, with Kubernetes and
kubectl v1.34.0. These are real command transcripts, not new native Terminal screenshots.
LoadBalancer external-address/tunnel verification and optional TLS remain pending.

## September 17 history

There was no configured Kubernetes context during the initial local validation. Those checks
did not create or modify a cluster or perform database, AWS, or Terraform operations.

The student's subsequent live run created a local Minikube cluster but failed before creating
the first Pod. The [original screenshot, diagnosis, and resume command](evidence/startup-race/README.md)
document the default ServiceAccount startup race. A later read-only check found the node Ready
and the default ServiceAccount present. A [resumed student run](evidence/live-checkpoints/README.md)
then passed the node, CoreDNS, ServiceAccount, and client Pod waits. After resolving the
screenshot-picker conflict, the student saved an actual Terminal screenshot and ran the
session 10 scaling/update/rollback commands. The immediate HTTP check after rollback failed,
stopping the runner before its session 10 screenshot and sessions 11–12. A separate recorded
read-only follow-up found ready workloads and fetched the restored `Hello from v1` response.

Four [recorded command-output images and their raw transcripts](evidence/local-validation/README.md)
remain embedded in the session READMEs. These are images rendered from the September command
output; they are not native Terminal screenshots. Original Terminal screenshots and raw live
logs are separately linked in [live evidence](evidence/live-checkpoints/README.md).
The runner has readiness waits, screenshot retry/manual PNG recovery, and bounded HTTP/DNS
read retries. Syntax and 12 isolated regression checks passed at that time. The October
transcripts above now supply the later live checks; the original failures remain preserved.

## 1. September strict Kubernetes schemas

Used kubeconform **v0.8.0**, with its release archive checked against the publisher's SHA-256
checksum, and Kubernetes **1.34.0** schemas. The client available locally was kubectl **v1.34.1**.
The schema version is a validation target, not a claim about a running server's version.

Command from the repository root:

```bash
kubeconform -strict -summary -kubernetes-version 1.34.0 kubernetes-fundamentals kubernetes-core-objects kubernetes-services kubernetes-ingress-configmaps-secrets
```

Actual result:

```text
Summary: 43 resources found in 36 files - Valid: 43, Invalid: 0, Errors: 0, Skipped: 0
```

No resource schema was skipped. Deliberately broken lifecycle scenarios can be schema-valid:
their failure behavior must still be observed on a cluster.

## 2. September relationships and API behavior

The [validation script](scripts/validate-kubernetes.py) checks namespace consistency, workload
selectors, named Service target ports, Ingress references, ConfigMap names, the locally created
Secret's expected name/key, the StatefulSet's headless Service, and unchanged rollout selectors.
It also executes the Python source extracted from the actual ConfigMap with a temporary HTTP
server on loopback. The fixture value is public test data, not a credential.

Recorded results:

```text
PASS: 43 Kubernetes objects; namespaces, workload selectors, Service target ports, Ingress backends, ConfigMap references, external Secret contract, StatefulSet service, rollout selectors
PASS: API three success routes, three 404 routes, configuration values, secret presence/absence, and no secret-value disclosure
```

The success routes are `/api`, `/api/`, and `/api/health`. Direct requests to `/`, `/apix`, and
`/api/missing` return 404. A missing demonstration token produces `secret_loaded: false`; a
present token produces `true` without disclosing its value. These are application checks, not
proof of Kubernetes Secret injection or Ingress routing.

To repeat the checks, use Python 3 with PyYAML 6.0.3 in a virtual environment. For example:

```bash
python3 -m venv /tmp/devops-homework-validation
/tmp/devops-homework-validation/bin/python -m pip install PyYAML==6.0.3
/tmp/devops-homework-validation/bin/python scripts/validate-kubernetes.py
```

The script also verifies relative Markdown file links. It does not provision a cluster or call
the Kubernetes API. kubeconform can retrieve public schemas during validation; see its
[installation instructions](https://github.com/yannh/kubeconform#installation).

## 3. September actual container checks

Both session 12 images were pulled and their actual container commands were run in temporary
Docker containers with `--network none`. HTTP requests were issued inside each container over
loopback. The backend used the source extracted from `backend-code.yaml`, mounted read-only,
with demonstration environment values. All temporary test containers were removed afterward.

| Container | Observed result |
| --- | --- |
| `nginx:1.28-alpine` | `Hello from DevOps session 12 frontend` |
| `python:3.13-alpine` | API returned the JSON below from `/api/health`. |

```json
{"service": "DevOps session 12 API", "environment": "coursework", "log_level": "INFO", "currency": "INR", "secret_loaded": true}
```

Image digests recorded during the check:

```text
nginx@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236
python@sha256:7415fbc3c9e4979cc717d92377ab2bc7b2b4a2af1ac03cc52b5f3f88efedaf3a
```

The manifests use readable image tags for coursework. These digests identify the artifacts
tested on September 17; the tags can move later. BusyBox lifecycle drills were not executed
during these historical container checks; the October session 10 transcript records the later drills.

## 4. Current live evidence and remaining deliverables

| Topic | Captured | Still to capture on the disposable lab |
| --- | --- | --- |
| Fundamentals | October Ready node, CoreDNS, default ServiceAccount, ready client and healthy system Pods; historical September Terminal screenshot retained. | New October Terminal screenshot. |
| Session 10 | October ReplicaSet replacement; rolling v1→v2→rollback; blue/green endpoint switch; stable+canary HTTP; recreate replacement; all 12 lifecycle/probe/init/sidecar/termination drills. | New Terminal screenshots. |
| Session 11 | October ClusterIP/NodePort HTTP; ExternalName/headless and stable Pod DNS; LoadBalancer internal Service HTTP; broken-selector failure and restored traffic. | Required LoadBalancer external address/tunnel connectivity and new screenshots. |
| Session 12 | October ConfigMap/Secret presence, frontend/API HTTP Ingress, configuration reload after restart, broken Ingress 503→recovery, and public newline fixture. | New Terminal screenshots; optional TLS exercise. |

Each session README links the October transcripts and retains reproducible commands and expected observations.
Those expectations must not be submitted as actual command output. Save real output or
screenshots from the lab, review the [form answer sheet](SUBMISSION.md), and then submit the form.
