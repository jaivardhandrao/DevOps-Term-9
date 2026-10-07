# Actual October 7 local evidence

These are agent-executed command transcripts from a newly created, isolated Minikube `devops-oct7` cluster (Kubernetes v1.34.0, matching kubectl v1.34.0). They are actual output, not expected-output examples and not native Terminal screenshots. Original September evidence is preserved separately.

| Session | Observed result | Remaining |
| --- | --- | --- |
| 9 | Ready node, CoreDNS, default ServiceAccount, ready client, healthy system Pods | New Terminal screenshot not captured |
| 10 | ReplicaSet replacement; rolling v1→v2→rollback; blue/green endpoint switch; stable+canary HTTP; recreate replacement; all 12 lifecycle/probe/init/sidecar/termination drills | New Terminal screenshots not captured |
| 11 | ClusterIP/NodePort HTTP; ExternalName and headless DNS; LoadBalancer internal Service HTTP; broken selector produced no endpoints and failed HTTP, restoration recovered traffic | LoadBalancer external address remains pending; external/tunnel connectivity and screenshots not captured |
| 12 | API-server label rejection found and fixed; ConfigMap and Secret presence; frontend+API Ingress; configuration changes visible after restart; broken Ingress503→restored API; public newline fixture reproduction | New Terminal screenshots not captured; optional TLS not exercised |

## Exact transcripts

### session-10

- [20261007T101438Z.txt](session-10/20261007T101438Z.txt) — completed checks.

### session-11

- [20261007T101710Z.txt](session-11/20261007T101710Z.txt) — failed attempt retained; superseded by later completed run.
- [20261007T101841Z.txt](session-11/20261007T101841Z.txt) — completed checks.

### session-12

- [20261007T101720Z.txt](session-12/20261007T101720Z.txt) — failed attempt retained; superseded by later completed run.
- [20261007T101851Z.txt](session-12/20261007T101851Z.txt) — failed attempt retained; superseded by later completed run.
- [20261007T102115Z.txt](session-12/20261007T102115Z.txt) — completed checks.

### session-9

- [20261007T101114Z.txt](session-9/20261007T101114Z.txt) — completed checks.

## Reproduce

Use an explicit disposable context whose API server is on localhost. The driver refuses other endpoints and never uses the current context implicitly:

```bash
python3 scripts/run-coursework-labs.py --context devops-oct7 --session 9
python3 scripts/run-coursework-labs.py --context devops-oct7 --session 10
python3 scripts/run-coursework-labs.py --context devops-oct7 --session 11
python3 scripts/run-coursework-labs.py --context devops-oct7 --session 12
```

The scripts create and alter only coursework resources in `devops-homework`. The operator must create the disposable cluster first and install its Ingress controller for session12. Runs write timestamped output files and stop on unmet assertions. Failed attempts stay alongside successful reruns. They do not provision cloud infrastructure.

The first session12 attempt exposed a label with spaces (`version: DevOps session 12 frontend`). The fixed label is `session-12-frontend`; the application page text is unchanged. A later attempt exposed asynchronous Ingress endpoint propagation after rollout. The driver now waits for the intended configuration content and for the deliberately broken route's503 response, preserving all observed retries.

The first session11 attempt recorded BusyBox resolving the requested short name but returning nonzero on later search-list candidates. The corrected run retains that diagnostic and uses absolute DNS queries for unambiguous success checks.

## Genuine GitHub Actions screenshots

Captured from the live GitHub website on October 7 in a newly opened browser tab:

- [Run summary](screenshots/github-actions-success-37609532257.jpg) shows **Success**, pull request **#4**, branch `homework/october-7-completion`, and the **Assignment tests and static checks** workflow. [Source run](https://github.com/jaivardhandrao/DevOps-Term-9/actions/runs/37609532257).
- [Completed checks job](screenshots/github-actions-job-112753122569.jpg) shows the successful job and its actual steps: capture-recovery tests using fake CLIs, Kubernetes reference validation, SQLite backend tests, frontend tests/build, and offline Helm lint/render/probe checks. [Source job](https://github.com/jaivardhandrao/DevOps-Term-9/actions/runs/37609532257/job/112753122569).

These unaltered browser screenshots prove this tests/static-checks run succeeded. They do **not** establish execution of the full security/CD workflow, registry publication, a Kubernetes deployment, or the session 9–12 live behaviors. They are **not native Terminal screenshots** and do not close that remaining coursework requirement. GitHub displayed one non-failing Node.js 20 action-runtime deprecation warning in the successful run.

A fresh Codex Terminal was requested for native capture, but the app queued the request for this worker's hidden thread instead of exposing a new visible terminal surface. Existing private Terminal windows were not inspected, no accessibility settings were changed, and no terminal image was fabricated.
