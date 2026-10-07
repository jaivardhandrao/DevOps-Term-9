# Actual October 7 local evidence

These are agent-executed command transcripts from a newly created, isolated Minikube `devops-oct7` cluster (Kubernetes v1.34.0, matching kubectl v1.34.0). They are actual output, not expected-output examples and not native Terminal screenshots. Original September evidence is preserved separately.

| Session | Observed result | Remaining |
| --- | --- | --- |
| 9 | Ready node, CoreDNS, default ServiceAccount, ready client, healthy system Pods; genuine earlier node/client screenshot retained | Current-run output screenshots not captured; the homework does not prescribe a new capture date |
| 10 | ReplicaSet replacement; rolling v1→v2→rollback; blue/green endpoint switch; stable+canary HTTP; recreate replacement; all 12 lifecycle/probe/init/sidecar/termination drills | New Terminal screenshots not captured |
| 11 | ClusterIP/NodePort HTTP; ExternalName and headless DNS; LoadBalancer internal Service HTTP; broken selector produced no endpoints and failed HTTP, restoration recovered traffic; actual outputs satisfy the allowed output/screenshots format | LoadBalancer external address remains pending; external/tunnel connectivity not captured |
| 12 | API-server label rejection found and fixed; ConfigMap and Secret presence; frontend+API Ingress; configuration changes visible after restart; broken Ingress503→restored API; public newline fixture reproduction; genuine current frontend browser screenshot | API and before/after troubleshooting screenshots missing; browser API display blocked; optional TLS not exercised |

## Exact transcripts

### Fresh current-state observers

The [live observer](live-verify.py) executes actual commands against the explicitly supplied
isolated `devops-oct7` kubeconfig and refuses a non-loopback Kubernetes API. It performs
resource reads, rollout-history reads and HTTP/DNS requests. Session 12 opens an automatically
allocated loopback Ingress port-forward and stops only that process; no lab objects are changed.

- [Session 9 current state](session-9/current-state.txt): Ready node, system Pods, ServiceAccount and DNS client.
- [Session 10 current state](session-10/current-state.txt): workload readiness, retained rollout history, EndpointSlices, current v1/green HTTP routes.
- [Session 11 current state](session-11/current-state.txt) and [DNS](session-11/current-dns.txt): Service types, ready StatefulSet identities, current internal HTTP paths and DNS answers. External LoadBalancer remains pending.
- [Session 12 current state](session-12/current-state.txt): ready workloads, non-sensitive configuration and Secret presence, current frontend/API HTTP Ingress.

These files are genuine fresh command output, not replayed historical logs. They show current
state rather than repeating the original mutation/failure transitions. Native screenshots,
when captured separately, must be captioned with that same limitation.

From the repository root, with `LAB_KUBECONFIG` set to the isolated kubeconfig:

```bash
python3 evidence/october-7/live-verify.py 9 --kubeconfig "$LAB_KUBECONFIG" --context devops-oct7
python3 evidence/october-7/live-verify.py 10 --kubeconfig "$LAB_KUBECONFIG" --context devops-oct7
python3 evidence/october-7/live-verify.py 11 --kubeconfig "$LAB_KUBECONFIG" --context devops-oct7
python3 evidence/october-7/live-verify.py 11 --view dns --kubeconfig "$LAB_KUBECONFIG" --context devops-oct7
python3 evidence/october-7/live-verify.py 12 --kubeconfig "$LAB_KUBECONFIG" --context devops-oct7
```

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

On the later coverage pass, the dedicated screenshot worker attempted the native Terminal
app through the computer-use interface. Access to Terminal was explicitly blocked by that
interface's safety restriction. No alternative automation path was used to bypass the block.
The current-state observers above were executed normally through the authorized command tool;
their transcripts are valid runtime evidence, but native Terminal screenshots remain pending.

## Genuine session 12 frontend browser screenshot

The [actual frontend image](screenshots/session-12-live-frontend.jpg) shows the current
`Hello from DevOps session 12 frontend` response. A new loopback port-forward and the
[GET-only relay](serve-session12-view.py) supplied the actual Ingress's required host header;
the response bytes were passed unchanged. This is a live application screenshot, not a
rendered transcript or a fault/TLS demonstration.

[Capture notes](session-12/browser-capture.md) record the browser API-route block and successful
CLI HTTP 200 header observation. No new fault was introduced, no protection was bypassed,
and only the owned relay/forward were stopped. The earlier real 503→200 troubleshooting
transcript is preserved, while its missing before/after screenshots remain explicit.
