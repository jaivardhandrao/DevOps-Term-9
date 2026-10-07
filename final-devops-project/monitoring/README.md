# TaskBoard monitoring

Prometheus scrapes the API every five seconds. A blackbox HTTP probe checks `/ready`, including database/schema availability. Grafana provisions the TaskBoard dashboard automatically. A scrape success alone does not prove database readiness.

Metrics include request count/status, latency histogram, process CPU seconds and resident memory. CPU is a rate in cores; memory is bytes. These process metrics are not node-wide utilization. The isolated cluster's metrics-server provides per-container CPU/memory for `kubectl top pods` and HPA.

## Local Kubernetes

Create namespace `monitoring-oct7` and a private `grafana-admin` Secret with key `password`. Generate it from a protected temporary password file; do not echo or commit it. Then:

```sh
kubectl -n monitoring-oct7 create configmap monitoring-config \
  --from-file=prometheus.yml --from-file=alerts.yml --from-file=blackbox.yml \
  --from-file=grafana-datasource.yml --from-file=grafana-dashboard-provider.yml \
  --from-file=taskboard-dashboard.json --dry-run=client -o yaml | kubectl -n monitoring-oct7 apply -f -
kubectl -n monitoring-oct7 apply -f stack.yaml
kubectl -n monitoring-oct7 rollout status deployment/prometheus
kubectl -n monitoring-oct7 rollout status deployment/grafana
kubectl -n monitoring-oct7 port-forward --address 127.0.0.1 svc/prometheus 19090:9090
# In another terminal:
kubectl -n monitoring-oct7 port-forward --address 127.0.0.1 svc/grafana 13000:3000
```

Open `http://127.0.0.1:13000/d/taskboard`. Anonymous access is Viewer only and intended for this loopback coursework environment. Admin password comes from the Secret; signup and the login form are disabled. No Ingress/LoadBalancer is created for monitoring. Do not expose these services publicly.

Prometheus alerts are visible at `http://127.0.0.1:19090/alerts`. No email/Slack receiver is configured: firing an alert does not contact anyone.

## Compose

From `final-devops-project`, set `GRAFANA_ADMIN_PASSWORD_FILE` to a private generated file and run:

```sh
docker compose -f compose.yaml -f monitoring/compose.monitoring.yaml up -d
```

The override uses service DNS (`backend`) rather than Kubernetes DNS. It does not replace the application compose file.

## Observe and investigate

```sh
kubectl -n capstone-oct7 logs deployment/backend --tail=50
kubectl -n capstone-oct7 top pods
curl -fsS 'http://127.0.0.1:19090/api/v1/query?query=up'
curl -fsS 'http://127.0.0.1:19090/api/v1/alerts'
```

Metrics reveal trends; logs preserve individual request/failure records. Traces follow one request across services and would identify which downstream span is slow. This app supplies metrics and container logs; it does not claim a deployed OpenTelemetry collector or distributed tracing backend.

See [the troubleshooting runbook](../troubleshooting/README.md) for a controlled Service-selector fault that demonstrates alerts and recovery without corrupting data.
