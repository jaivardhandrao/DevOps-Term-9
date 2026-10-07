# Session 14 — Kubernetes troubleshooting

Nine required issue types are demonstrated in the dedicated `devops-advanced` namespace, alongside a two-replica Nginx mini-project. The approach is: observe status, inspect events and logs, form a specific hypothesis, change the relevant configuration, then retest the failed behavior.

**Execution status (October 7, 2026): implementation prepared; live scenarios not executed.** Automatic approval review blocked local cluster mutation under the earlier read-only task scope. The table below describes planned reproducible failure/fix cases, not observed runtime results. See [evidence status](evidence/README.md).

[The lab driver](../kubernetes-storage-hpa-probes/run-lab.py) records actual commands, output and exit codes into `evidence/troubleshooting-run.txt` when authorized to execute. No such successful record currently exists. The small broken and corrected Pod definitions are in [scenarios/](scenarios/); JSON is accepted as a Kubernetes manifest.

## Reproduce

Run Session 13 first to create the namespace and the `volume-examples` diagnostic client, then:

```bash
python3 kubernetes-storage-hpa-probes/run-lab.py troubleshooting
```

It requires the named `devops-oct7` context and a local API endpoint. Use a fresh disposable namespace for a new recording; some commands intentionally fail and their actual exit codes are recorded. The runner deletes only its named `trouble-*` Pods when an immutable Pod field must change. It leaves the corrected application for inspection.

## Issues, investigation and fixes

| Issue | Deliberate cause | Investigation | Fix and verification |
|---|---|---|---|
| CrashLoopBackOff | Shell prints an error and exits 1 | `get pod`, `describe`, `events`, `logs --previous` | Replace with a long-running command; wait Ready and read healthy log |
| ErrImagePull | `busybox:devops-intentionally-missing` tag does not exist | Capture the first pull error and registry message in events | Use valid `busybox:1.36.1`; verify Ready |
| ImagePullBackOff | Kubelet retries the same failed pull with backoff | Wait for the waiting reason to transition; inspect events | Same image correction; this is a later stage of the same root cause, not a second invented problem |
| Pending | Node selector requires a nonexistent `devops-lab` label | `describe pod` shows scheduler rejection | Remove the invalid node selector in the fixed manifest; verify Pod scheduled and Ready |
| ContainerCreating | Required ConfigMap-backed volume is absent | `describe` / events show `FailedMount` | Create the missing ConfigMap and verify `/config/MODE` reads `repaired` |
| Service connectivity | Service selector uses `app: wrong-app` | Compare Pod labels, Service selector and empty EndpointSlice | Restore `app: trouble-web`; retest HTTP through the Service |
| DNS | Pod's custom resolver points to documentation-only IP 192.0.2.1 | `nslookup` times out while app itself is healthy | Restore normal ClusterFirst DNS; resolve the full Service name |
| Pod networking | HTTP server binds only 127.0.0.1 | Local loopback works but a different Pod cannot reach its Pod IP | Bind to 0.0.0.0; verify remote Pod-to-Pod HTTP |
| Configuration | Required `MODE` environment variable references an absent ConfigMap | Observe CreateContainerConfigError and events | Create the ConfigMap and verify `printenv MODE` |

The Pod-networking case diagnoses an application bind address rather than changing the CNI or global firewall. The DNS test changes one Pod only. This keeps deliberate failures contained and makes their root causes distinct.

## Commands practiced

| Command | What it answers |
|---|---|
| `kubectl get pods` | Which Pods are ready, waiting or restarting? |
| `kubectl get pods -o wide` | Which node and Pod IP were assigned? |
| `kubectl describe pod` | What were the configuration, conditions and recent events? |
| `kubectl logs --previous` | What did the last crashed container print? |
| `kubectl exec` | Does the process/configuration/DNS/HTTP behavior work inside a Pod? |
| `kubectl events --for pod/NAME` | What attempts did Kubernetes make for this object? |
| `kubectl get events --sort-by=.lastTimestamp` | What happened across the namespace over time? |
| `kubectl explain pod.spec.containers.resources` | What does the API schema say this field means? |
| `kubectl top pods` | What CPU and memory does the metrics API currently report? |

## Mini-project answers

The [mini-project](mini-project.yaml) has a Deployment with two Nginx replicas and a ClusterIP Service. The broken-image Pod supplies the image failure challenge. The driver records `get`, `describe` and events **before** replacing it. The image tag is the root cause; a Pod name or Service change cannot repair an unavailable image.

For the Service challenge, both Nginx Pods can be healthy while the Service has no usable endpoints. Selectors match labels exactly: restoring `app: trouble-web` reconnects the Service to those Pods. The verification is a successful HTTP request through the Service, not merely a successful `kubectl apply`.

1. `get` is a concise state summary; `describe` adds conditions, configuration and events.
2. Logs explain application behavior. Events explain what the scheduler, kubelet and controllers attempted; neither replaces the other.
3. Use `exec` for a focused check in a running container, such as an environment value or local HTTP response. It cannot help before the container starts.
4. CrashLoopBackOff is retry backoff after repeated container exits. It is a symptom; the preceding logs/exit code identify the cause.
5. ImagePullBackOff is backoff after failed image retrieval. Check spelling, tags, registry availability and authorization without printing credentials.
6. A Pod can stay Pending because its resource requests, affinity/selectors, taints or volume constraints cannot be satisfied.
7. A Service can have no ready endpoints because selectors mismatch or every matching Pod is unready.
8. A Service forwards to ready matching Pod IPs; it does not itself create Pods. The Deployment manages replicas.
9. Kubernetes DNS lets Pods discover Services by names such as `trouble-web.devops-advanced.svc.cluster.local`.
10. `Running` means containers have been started; readiness determines traffic eligibility, so HTTP testing remains necessary.

## Evidence status

The execution record is the authority for what was actually observed. An interrupted run does not prove later cases. No fabricated screenshot is included; the homework's separate screenshot requirement remains a presentation item unless actual screen captures accompany this record.

References: [debug running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/), [debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/), [debug DNS](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/).
