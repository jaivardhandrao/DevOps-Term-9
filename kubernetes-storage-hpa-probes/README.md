# Session 13 — Storage, HPA and probes

This submission implements a small Python HTTP application, persistent storage, CPU-based scaling and three health probes. It follows the session mini-project's two-to-five replica range and 50% CPU target, with smaller resource requests for a disposable local cluster.

**Execution status (October 7, 2026): incomplete.** The four application routes passed a real local HTTP smoke check. The initial Kubernetes run stopped at its context guard before creating any workloads; after correcting the guard, automatic approval review rejected cluster execution. PVC persistence, HPA scale-up/down and the readiness failure exercise have therefore **not been observed**. See [the evidence inventory](evidence/README.md). The manifests and runner are prepared for an authorized rerun.

## Files and architecture

```text
Client -> Service advanced-web:80 -> Python web Pods:8080 (2–5)
                                     | /health: startup + liveness
                                     | /ready: readiness
                                     | /work: bounded CPU computation
                                     + /data -> PVC advanced-data -> standard StorageClass
Metrics Server -> CPU metrics -> HPA -> Deployment replica count
```

- [Volume concepts and practical examples](01-kubernetes-volumes/README.md).
- [Original application](app/server.py); no third-party Python dependencies.
- [Mini-project manifests](mini-project/): Namespace, ConfigMap, Deployment, Service and 500 MiB PVC.
- [hpa.yml](hpa.yml): `autoscaling/v2`, CPU utilization target 50%, minimum 2 and maximum 5 replicas.
- [Load generator](load-generator.yaml): four request loops, resource limits, maximum lifetime 240 seconds.
- [Lab driver](run-lab.py): context guard, command/output capture, persistence and scaling assertions.
- [Initial guarded execution record](evidence/storage-run.txt) and [HTTP smoke check](evidence/http-smoke.txt). These are agent-operated terminal outputs, not a claim that the student manually ran them.

## Reproduce

Use a fresh, disposable Minikube profile called `devops-oct7` with the `standard` StorageClass and Metrics Server enabled. Set `KUBECONFIG` to that profile's dedicated kubeconfig. The runner explicitly selects `devops-oct7` and refuses a non-local API endpoint; it never changes the current context.

```bash
kubectl --context devops-oct7 get nodes
kubectl --context devops-oct7 get --raw /apis/metrics.k8s.io/v1beta1/nodes
python3 kubernetes-storage-hpa-probes/run-lab.py storage
```

The script applies the app, waits for readiness, writes a marker to the PVC, deletes one owned Pod and verifies the marker on all replacement/current Pods. It creates an `emptyDir`/node-local `hostPath` example and tests the HTTP Service from that Pod. Then it applies the load Job and records:

```bash
kubectl -n devops-advanced get hpa
kubectl -n devops-advanced get pods
kubectl -n devops-advanced top pods
kubectl -n devops-advanced describe hpa advanced-web
```

It stops only its `advanced-load` Job, tests a controlled readiness failure, restores readiness, and records scale-down observations. The healthy application remains available for review. A failed assertion is a failed lab; the runner does not invent expected output.

## Design choices and lessons

CPU utilization is relative to the CPU **request**, not the limit or whole node. A 25m request and 50% target means the target is approximately 12.5m per Pod. `/work` performs PBKDF2 computation so HTTP load measurably consumes CPU. `/health` and `/ready` remain cheap. The Pod limit is 200m; five app Pods are capped at one CPU collectively. HPA needs a working metrics API and must tolerate its initial sampling delay.

The 60-second scale-down stabilization window is intentionally shorter than the common five-minute default for this lab. Scaling is sampled, so observations vary with metrics timing; the evidence records actual values rather than promised percentages.

| Probe | Purpose | Failure behavior in this app |
|---|---|---|
| Startup | Wait for HTTP initialization | Restarts only after 30 failed checks at two-second intervals; other probes are gated until success |
| Readiness | Decide whether to receive Service traffic | `/tmp/not-ready` makes `/ready` return 503; removes this Pod from ready endpoints without restarting it |
| Liveness | Detect an unhealthy running process | Repeated `/health` failures trigger a container restart |

The readiness test deliberately changes only a temporary marker. Inspect EndpointSlice `conditions.ready` before restoring the marker; `Running` alone does not mean ready to serve.

The mini-project shares one ReadWriteOnce PVC across replicas **only on this single Minikube node**. RWO means read/write mounting by one node, not necessarily one Pod. This is not a portable multi-node shared-write design. A production deployment would use an appropriate ReadWriteMany backend or independent claims with a StatefulSet, depending on its data model. No claim is made that this teaching deployment is production-ready.

## Validation status

The dated [execution record](evidence/storage-run.txt) shows the initial guard failure; it is not persistence or autoscaling evidence. Those runtime requirements remain incomplete until a complete successful lab record is captured. No screenshot has been synthesized from expected output.

## References

- [Instructor Session 13 mini-project](https://github.com/Nency-Ravaliya/devops-heros/tree/main/session-13-storage-hpa-probes/mini-project)
- [Kubernetes HPA walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)
- [Kubernetes volume concepts](https://kubernetes.io/docs/concepts/storage/volumes/)
- [Probe configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
