# Session 13 evidence inventory

| Record | Actual result |
|---|---|
| [http-smoke.txt](http-smoke.txt) | `/`, `/health`, `/ready`, `/work` returned HTTP 200 using the exact application handler on an ephemeral localhost port |
| [storage-initial-context-guard.txt](storage-initial-context-guard.txt) | Earlier run stopped because the dedicated kubeconfig had no current-context; no workload was created |
| [storage-namespace-order-failure.txt](storage-namespace-order-failure.txt) | First newly authorized attempt exposed namespace ordering; fixed by applying the namespace first |
| [storage-run.txt](storage-run.txt) | PVC replacement persistence, volume examples, HTTP response, CPU load, HPA 2→5, readiness failure/recovery; original scale-down observation timed out |
| [scale-down-follow-up.txt](scale-down-follow-up.txt) | Read-only follow-up verified automatic 5→2 recovery, two Ready Pods and 8% CPU against the 50% target, without changing HPA or replicas |

The runner now checks for the explicitly named `devops-oct7` context and a local API endpoint. Every Kubernetes action supplies `--context devops-oct7`; it does not change the user's current context.

The practical requirements above are observed in the actual records. The load Job was deleted and the healthy app/PVC remain for review. Earlier approval blocks were superseded by the later explicit authorization; they are historical, not the current runtime status.

Actual Terminal screenshots remain unavailable: the CUA tool rejected access to `com.apple.Terminal` for safety reasons. A direct browser navigation to the app's own loopback port also returned `ERR_BLOCKED_BY_CLIENT`. Neither restriction was bypassed and no log rendering was substituted. [capture-live-state.sh](capture-live-state.sh) contains compact read-only commands for a later permitted Terminal capture.
