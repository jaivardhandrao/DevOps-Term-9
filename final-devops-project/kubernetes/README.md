# TaskBoard Kubernetes deployment

The authoritative resources live in [the Helm chart](../helm/taskboard/). The rendered example below is for **initial installation only** into a new disposable namespace. Use [Helm upgrades](../helm/README.md) or [Argo CD reconciliation](../gitops/README.md) for later releases.

```sh
helm template taskboard ../helm/taskboard -n capstone-oct7 > taskboard.yaml
kubectl -n capstone-oct7 apply -f taskboard.yaml
kubectl -n capstone-oct7 wait --for=condition=complete job/taskboard-migrate-1 --timeout=240s
kubectl -n capstone-oct7 rollout status deployment/backend
kubectl -n capstone-oct7 rollout status deployment/frontend
```

Create the namespace and `taskboard-db` Secret first. Its `password` key must hold a generated local password; never commit the value. Services are ClusterIP. Optional Ingress routes a local hostname to frontend, which proxies the API. Access from the laptop through a loopback port-forward.

The chart includes Deployments, Services, ConfigMap, existing Secret mounts, HPA, startup/readiness/liveness probes, PostgreSQL StatefulSet and PVC. Each workload runs as non-root with dropped capabilities and no service-account token. Readiness checks the database and schema; liveness checks the process so a database outage does not cause restart loops.

`taskboard.yaml` is a generated example, not independent configuration. Re-render to inspect changes, but do not apply later releases over this initial installation: plain `helm template` fixes `.Release.Revision` at 1, so the completed `taskboard-migrate-1` Job cannot accept a changed pod template and would not rerun migrations. Helm manages revision-specific Jobs; Argo manages the migration Sync hook. Select one release owner before upgrades. The example Secret deliberately contains no credentials and is not applied automatically.


## Verified isolated deployment

October 7 runtime checks in `devops-oct7` / `capstone-oct7` passed [CRUD, proxy, readiness and validation](evidence/2026-10-07/crud-smoke-patched-images.txt). A [persistence test](evidence/2026-10-07/persistence.json) recreated the PostgreSQL Pod, confirmed the PVC UID stayed the same, and read the previously created task successfully. The temporary task was removed after verification.

The backend and frontend were then rolled to patched builds. [Runtime image IDs](evidence/2026-10-07/patched-runtime-images.json) match the image-build config digests and link to the scan reports with zero HIGH/CRITICAL findings. PostgreSQL and its PVC were retained. A loopback port-forward must be restarted after its selected frontend Pod is replaced; the failed old tunnel was reconnected before the passing smoke check.

The first PostgreSQL start hit `ImagePullBackOff` because the node could not resolve Docker’s image CDN. Loading the same `postgres:17-alpine` image from the local Docker image store resolved the transport issue; the migration Job then completed. Argo CD subsequently adopted the resources and owns reconciliation, as recorded in [GitOps evidence](../gitops/README.md).
