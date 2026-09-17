# Session 10: Kubernetes Pods, ReplicaSets & Deployments

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117
- **Status:** Core workload, scaling, update, and rollback logs captured. Session screenshot and additional strategy/lifecycle evidence pending.

Complete the [local lab setup](../kubernetes-fundamentals/README.md#local-lab-setup) first.
Run the following commands from this folder. Each exercise uses distinct labels so a standalone
Pod, ReplicaSet, and Deployment do not accidentally select each other's Pods.

## Core objects

| Object / file | Purpose | What to verify on the cluster |
| --- | --- | --- |
| [Pod](pod.yaml) | One independently managed Pod. | It becomes ready; deleting it does not create a replacement. |
| [ReplicaSet](replicaset.yaml) | Keeps two matching Pods available. | Scaling or deleting a managed Pod triggers reconciliation. |
| [Deployment v1](deployment-v1.yaml) | Manages ReplicaSets and three ready replicas. | A Pod-template update creates a new ReplicaSet. |
| [Deployment v2](deployment-v2.yaml) | Changes the template's version label and page text. | Page response changes from `v1` to `v2`. |
| [Service](service.yaml) | Routes to ready `core-web` Pods. | Port 80 targets the named container port `http`. |
| [DaemonSet](daemonset.yaml) | Runs a simple agent on eligible nodes. | Desired count follows eligible nodes, rather than a replica setting. |
| [StatefulSet](../kubernetes-services/headless.yaml) | Demonstrates stable numbered Pod identities in session 11. | Pods are named `stateful-web-0` and `stateful-web-1`. No database is deployed. |

```bash
kubectl --context=devops-coursework -n devops-homework apply -f pod.yaml -f replicaset.yaml -f deployment-v1.yaml -f service.yaml
kubectl --context=devops-coursework -n devops-homework wait --for=condition=Ready pod/standalone-web --timeout=120s
kubectl --context=devops-coursework -n devops-homework rollout status deployment/core-web --timeout=120s
kubectl --context=devops-coursework -n devops-homework get pods,replicasets,deployments -o wide
kubectl --context=devops-coursework -n devops-homework scale replicaset/replica-web --replicas=3
kubectl --context=devops-coursework -n devops-homework delete pods -l app=replica-web
kubectl --context=devops-coursework -n devops-homework get pods -l app=replica-web -w
```

Stop the watch with Ctrl+C after replacement Pods become ready. Compare names and creation
times before/after deletion. The Deployment's selector stays stable across versions; the
template changes. Changing only replica count does not create a rollout revision.

## Rolling update and rollback

In one terminal, forward the Service. In another, run curl and the update commands below:

```bash
kubectl --context=devops-coursework -n devops-homework port-forward service/core-web 8082:80
```

```bash
curl --fail http://localhost:8082/
kubectl --context=devops-coursework -n devops-homework apply -f deployment-v2.yaml
kubectl --context=devops-coursework -n devops-homework rollout status deployment/core-web --timeout=120s
kubectl --context=devops-coursework -n devops-homework get pods -l app=core-web --show-labels
kubectl --context=devops-coursework -n devops-homework rollout history deployment/core-web
kubectl --context=devops-coursework -n devops-homework rollout undo deployment/core-web
kubectl --context=devops-coursework -n devops-homework rollout status deployment/core-web --timeout=120s
```

Restart port-forward after each rollout, then curl again: it attaches to one Pod and can stop
when that Pod is replaced. It is useful for checking page content, not for proving Service
load balancing or uninterrupted traffic. The manifests use `maxSurge: 1`, `maxUnavailable: 0`,
and a readiness probe; application compatibility and cluster capacity still affect availability.

## Other release strategies

| Strategy | Included files | Exercise |
| --- | --- | --- |
| Blue/green | [Two Deployments and one Service](strategies/blue-green.yaml) | Wait for both versions, then change the Service's `slot` selector. |
| Canary | [Three stable Pods and one canary](strategies/canary.yaml) | One Service selects both tracks. Approximate distribution follows endpoints and connection behavior, not a guaranteed 75/25 request split. |
| Recreate | [v1](strategies/recreate-v1.yaml), [v2](strategies/recreate-v2.yaml) | Old replicas terminate before new version replicas start; expect an availability gap. |

```bash
kubectl --context=devops-coursework -n devops-homework apply -f strategies/blue-green.yaml
kubectl --context=devops-coursework -n devops-homework rollout status deployment/web-blue --timeout=120s
kubectl --context=devops-coursework -n devops-homework rollout status deployment/web-green --timeout=120s
kubectl --context=devops-coursework -n devops-homework get endpointslices -l kubernetes.io/service-name=blue-green -o wide
kubectl --context=devops-coursework -n devops-homework patch service blue-green --type=merge -p '{"spec":{"selector":{"app":"blue-green","slot":"green"}}}'
kubectl --context=devops-coursework -n devops-homework get endpointslices -l kubernetes.io/service-name=blue-green -o wide
kubectl --context=devops-coursework -n devops-homework apply -f strategies/canary.yaml
kubectl --context=devops-coursework -n devops-homework rollout status deployment/web-stable --timeout=120s
kubectl --context=devops-coursework -n devops-homework rollout status deployment/web-canary --timeout=120s
kubectl --context=devops-coursework -n devops-homework get endpointslices -l kubernetes.io/service-name=canary-web -o wide
kubectl --context=devops-coursework -n devops-homework apply -f strategies/recreate-v1.yaml
kubectl --context=devops-coursework -n devops-homework rollout status deployment/recreate-web --timeout=120s
kubectl --context=devops-coursework -n devops-homework apply -f strategies/recreate-v2.yaml
kubectl --context=devops-coursework -n devops-homework rollout status deployment/recreate-web --timeout=120s
```

Reapplying `blue-green.yaml` returns the Service selector to blue. Selector propagation and
existing connections mean the switch is not instantaneous. To inspect canary HTTP responses,
create session 11's client Pod, then run:

```bash
kubectl --context=devops-coursework -n devops-homework exec dns-client -- sh -c 'for i in 1 2 3 4 5 6 7 8 9 10; do wget -qO- http://canary-web; done'
```

## Pod lifecycle, probes, and debugging

Apply one lifecycle file at a time, inspect it, and delete it when done. Some files deliberately
fail. Do not recursively apply the whole session: version files are alternatives and failure
drills are separate exercises.

| File | Expected behavior to investigate |
| --- | --- |
| [01-running](lifecycle/01-running.yaml) | Long-running process; Running phase. |
| [02-pending](lifecycle/02-pending.yaml) | No node has the requested lab-only label; Pending. |
| [03-succeeded](lifecycle/03-succeeded.yaml) | Exit 0 with `restartPolicy: Never`; Succeeded phase. |
| [04-failed](lifecycle/04-failed.yaml) | Exit 1 with no restart; Failed phase. |
| [05-crashloop](lifecycle/05-crashloop.yaml) | Repeated failure with restart backoff. |
| [06-image-pull](lifecycle/06-image-pull.yaml) | Deliberately invalid registry; image pull failure/backoff. |
| [07-readiness](lifecycle/07-readiness.yaml) | Running but not ready until `/tmp/ready` exists. |
| [08-liveness](lifecycle/08-liveness.yaml) | Health file disappears after 20 seconds; restart count rises. |
| [09-startup](lifecycle/09-startup.yaml) | Startup probe tolerates the initial 20-second delay before liveness begins. |
| [10-init-container](lifecycle/10-init-container.yaml) | Init container writes a shared file before the app starts. |
| [11-multi-container](lifecycle/11-multi-container.yaml) | Two containers in one Pod, with separately selectable logs. |
| [12-termination](lifecycle/12-termination.yaml) | SIGTERM handler logs cleanup within the grace period. |

```bash
kubectl --context=devops-coursework -n devops-homework apply -f lifecycle/07-readiness.yaml
kubectl --context=devops-coursework -n devops-homework describe pod lifecycle-readiness
kubectl --context=devops-coursework -n devops-homework exec lifecycle-readiness -- touch /tmp/ready
kubectl --context=devops-coursework -n devops-homework wait --for=condition=Ready pod/lifecycle-readiness --timeout=60s
kubectl --context=devops-coursework -n devops-homework delete -f lifecycle/07-readiness.yaml
```

Use `kubectl describe pod` for events, `kubectl logs POD -c CONTAINER` for logs, and
`kubectl logs POD --previous` for the previous crashed container. The latter requires a previous
instance. Pod phases are Pending, Running, Succeeded, Failed, and Unknown. `CrashLoopBackOff`
and `ImagePullBackOff` are displayed waiting reasons, not additional Pod phases.

## Evidence to capture

The [actual student-run transcript](../evidence/live-checkpoints/02-session-10-partial.txt)
records Pod creation, ReplicaSet scaling/replacement, and v1 → v2 rollout responses. The
rollback completed, but its immediate HTTP check failed and stopped the capture script.
A [read-only follow-up](../evidence/live-checkpoints/02-session-10-follow-up.txt) records
ready workloads, rollout history, Service endpoints, and the restored `Hello from v1` response.
The session screenshot and additional strategy/lifecycle evidence remain pending.

The runner now retries failed HTTP reads for a bounded number of attempts after rollouts.
The original failure remains in the transcript; a successful rollout alone is not proof of
successful Service traffic. The images below show the earlier local validation checks.

![Actual manifest schema validation output](../evidence/local-validation/01-schema-validation.png)

![Actual API and manifest relationship checks](../evidence/local-validation/02-api-and-references.png)

[Raw logs and the live screenshot capture script](../evidence/local-validation/README.md)

Save actual Pod/ReplicaSet/Deployment output, replacement Pod names, rollout history, v1/v2
HTTP responses, Service endpoints before/after blue-green, and describe/log output from the
lifecycle drills. [Validation evidence](../KUBERNETES-VALIDATION.md) states what was checked here.
Delete individual resources using the same file paths, or remove the dedicated lab profile
after completing all sessions.

References: [instructor session 10](https://github.com/Nency-Ravaliya/devops-heros/tree/1a24fe08c4956db0f8f22ffd6655581f7185699e/session10-k8s-core-objects),
[Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/),
[Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/).
