# TaskBoard Helm deployment

Chart: [taskboard](taskboard/). Requires a Kubernetes cluster, a default StorageClass, locally loaded application images (or accessible registry images), and an existing database password Secret.

```sh
kubectl create namespace capstone-oct7
# Create a protected random password file locally, then:
kubectl -n capstone-oct7 create secret generic taskboard-db --from-file=password=/private/path/password
helm lint taskboard
helm upgrade --install taskboard taskboard -n capstone-oct7 --wait --wait-for-jobs --timeout 5m
kubectl -n capstone-oct7 get pods,services,pvc,hpa
kubectl -n capstone-oct7 port-forward --address 127.0.0.1 svc/frontend 18080:8080
```

Run these commands from this directory. The chart does not create credentials and never contains a real password. Backend and migration containers read the same mounted Secret file. The migration is a separate Job, not an implicit startup side effect in each replica. Failed database/schema readiness blocks traffic while preserving live processes.

The chart's default app image tags are `local`. CI overrides `backend.image.repository/tag/pullPolicy` and `frontend.image.repository/tag/pullPolicy` with immutable commit tags and loads them into its disposable kind cluster. Postgres runs as UID 70; the backend uses UID 10001 and frontend UID 101.

```sh
helm upgrade taskboard taskboard -n capstone-oct7 --set frontend.replicas=2 --wait --wait-for-jobs
helm history taskboard -n capstone-oct7
helm rollback taskboard 1 -n capstone-oct7 --wait
```

HPA requires metrics-server and CPU requests; it controls backend replicas. The chart omits backend `spec.replicas` when HPA is enabled so Helm/GitOps do not continually fight the autoscaler.

Ingress is opt-in:
```sh
helm template taskboard taskboard -n capstone-oct7 --set ingress.enabled=true
```
An Ingress controller and matching host routing are separately required; the default loopback port-forward works without either. Helm uninstall preserves StatefulSet PVCs; removing the disposable namespace destroys the coursework database.
