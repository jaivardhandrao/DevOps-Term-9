# GitOps reconciliation with Argo CD Core

The desired state is the [TaskBoard Helm chart](../helm/taskboard/). [application.yaml](application.yaml) selects the merged coursework repository branch `main`, namespace `capstone-oct7`, and locally loaded images. [project.yaml](project.yaml) restricts source repository, destination and resource kinds. It cannot deploy cluster-scoped resources.

Argo CD Core is pinned to **v3.5.4**, verified through the official release API on October 7, 2026. Core runs the application controller, repo-server and Redis without an API server/UI. ApplicationSet is scaled to zero because this demo has one Application. The installation includes CRDs and control-plane permissions; use only the newly created isolated cluster. Never install this coursework control plane into a shared or production cluster.

## Prerequisites

1. The chart has actually been pushed to the coursework repository’s `main` branch.
2. The cluster is the disposable `devops-oct7` context.
3. Namespaces `capstone-oct7` and `monitoring-oct7` exist.
4. App images tagged `local` have been loaded into that cluster.
5. A private `taskboard-db` Secret exists in `capstone-oct7`; credentials stay outside Git.

## Install and observe

```sh
kubectl --context devops-oct7 apply --server-side -k argocd-core/
kubectl --context devops-oct7 -n monitoring-oct7 rollout status deployment/argocd-repo-server --timeout=180s
kubectl --context devops-oct7 -n monitoring-oct7 rollout status statefulset/argocd-application-controller --timeout=180s
kubectl --context devops-oct7 apply -f project.yaml -f application.yaml
kubectl --context devops-oct7 -n monitoring-oct7 get application taskboard \
  -o jsonpath='{.status.sync.status}{" "}{.status.health.status}{" "}{.status.sync.revision}{"\n"}'
```

The status must actually report Synced/Healthy and a resolved Git commit before claiming success. Downloading the manifest, installing a controller, or creating an Application is insufficient evidence. A missing branch/chart yields a comparison error until the source is available.

The migration Job is an Argo Sync hook in wave 1; PostgreSQL is wave 0, application Deployments are wave 2, and HPA plus optional Ingress are wave 3. The migration runs before application rollout. HPA must follow its target Deployment: placing it in wave 0 would report `FailedGetScale` while the target does not exist and stop Argo from reaching the Deployment's wave. A working metrics-server is also required for HPA health. HPA controls backend replicas; the chart omits backend `spec.replicas` while HPA is enabled. Avoid concurrent manual Helm upgrades after Argo adoption; commit desired changes instead.

## Demonstrate drift correction

After Synced/Healthy, change a harmless ConfigMap field managed by the chart:

```sh
kubectl --context devops-oct7 -n capstone-oct7 patch configmap taskboard-config --type=merge \
  -p '{"data":{"APP_ENV":"intentional-drift"}}'
kubectl --context devops-oct7 -n capstone-oct7 get configmap taskboard-config -o jsonpath='{.data.APP_ENV}{"\n"}'
# Watch until the controller restores the value from Git:
kubectl --context devops-oct7 -n capstone-oct7 get configmap taskboard-config --watch
```

Record the deliberate drift, Argo's comparison/sync state and restored `APP_ENV=coursework`, plus the exact `.status.sync.revision`. Automatic self-healing is enabled; pruning is disabled to avoid deleting coursework resources or data during the demo.

The branch is intentionally mutable for this exercise. For a release, pin `targetRevision` and image tags/digests to reviewed immutable values. Credentials and persisted data are external state; never place them in the public repository.

## Verified runtime evidence

On October 7, Argo CD Core reconciled `main` at commit `a21851154ac1bf984ab7c7a0304073a19faac27d` and reported **Synced / Healthy**. A deliberately changed `APP_ENV=intentional-drift` was observed and automatically restored to `coursework`. See [initial reconciliation](evidence/2026-10-07/initial-reconciliation.json) and [the self-healing timeline](evidence/2026-10-07/drift-self-heal.json).

The first controller comparison exposed an installation namespace bug: the upstream ClusterRoleBinding names its service-account subject namespace `argocd`, and the overlay’s namespace transform did not rewrite that explicit field. The overlay now patches the subject to `monitoring-oct7`. No extra resource kinds or permissions were added beyond the pinned Core installation. After the correction, the controller could compare and reconcile live state. Backend HPA can briefly report missing CPU samples immediately after rollout; it became healthy once metrics-server had sampled the ready Pod.

The runtime uses the locally loaded, patched images recorded in [runtime image evidence](../kubernetes/evidence/2026-10-07/patched-runtime-images.json). Local tags are deliberately mutable for the lab; the evidence records config IDs and maps them to the build’s OCI index and scan report. A production deployment should use immutable image digests.

## References

- [Argo CD Core](https://argo-cd.readthedocs.io/en/stable/operator-manual/core/)
- [Declarative setup](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/)
- [Pinned release v3.5.4](https://github.com/argoproj/argo-cd/releases/tag/v3.5.4)
