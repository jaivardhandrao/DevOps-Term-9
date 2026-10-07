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
