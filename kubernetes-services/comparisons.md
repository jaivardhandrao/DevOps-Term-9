# Workload and networking object comparison

| Object | Responsibility | Scaling and updates | Typical use |
| --- | --- | --- | --- |
| Deployment | Reconcile a desired Pod template through ReplicaSets | Replica count, rolling update or recreate, rollout history | Stateless API or frontend |
| ReplicaSet | Maintain the selected number of matching Pods | Replaces missing Pods; no independent rollout strategy | Usually owned by a Deployment |
| DaemonSet | Place a Pod on every eligible node | Follows eligible nodes; supports rolling updates | Node log/metrics agent |
| StatefulSet | Maintain stable Pod identities and ordered management | Ordered numbered replicas and update controls | Stateful service requiring stable identities/PVCs |
| Service | Discover and route traffic to endpoints | Does not create, replace or scale Pods | Stable entry point while Pod IPs change |

A Deployment creates a new ReplicaSet when its Pod template changes; the old ReplicaSet
supports rollback. Updating a ReplicaSet alone does not orchestrate an application rollout.
The Deployment selector must match its template labels and must not overlap unrelated labs.

A Service needs ready endpoints selected by matching labels. Traffic reaches a Service port,
then a selected Pod's `targetPort`. A ReplicaSet can keep every Pod alive while a wrong Service
selector makes the application unreachable. A Service cannot restart a crashed application.

StatefulSet Pod names are stable (`stateful-web-0`, `stateful-web-1`); a headless Service supplies
their DNS identities. Volume claim templates can provide per-Pod persistent storage. The
session 11 Nginx example demonstrates naming only; session 13 and the final PostgreSQL
deployment demonstrate storage. Deployment Pods have interchangeable identities; DaemonSet
placement follows nodes rather than a desired replica count.

References: [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/),
[StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/),
[DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/),
[Services](https://kubernetes.io/docs/concepts/services-networking/service/).
