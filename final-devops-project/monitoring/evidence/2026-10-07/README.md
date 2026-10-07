# Actual monitoring evidence — October 7, 2026

Captured from the isolated `devops-oct7` context, namespace `monitoring-oct7`. Capture time is in [captured-at.txt](captured-at.txt).

- [Kubernetes status](kubernetes-status.txt): Prometheus, Grafana and blackbox exporter each have one ready Pod, zero restarts and ClusterIP services.
- [Grafana health](grafana-health.json): version 12.2.0 reports its local database healthy.
- [Dashboard readback](grafana-dashboard.json): the provisioned TaskBoard dashboard has seven panels.
- [Prometheus targets](prometheus-targets.json): Prometheus itself is up; the application target is down.
- [Readiness probe](prometheus-readiness.json): `probe_success=0` for the TaskBoard `/ready` endpoint.
- [Alerts](prometheus-alerts.json): `TaskBoardUnavailable` and `TaskBoardNotReady` are firing.

**Why the application is down:** the capstone API had not been deployed in this cluster at capture time. These alerts demonstrate missing-target detection, not a successful full application or fault-recovery exercise.

The blackbox scrape target itself is `up`: Prometheus can reach the exporter. That does **not** imply its HTTP readiness probe succeeded; `probe_success=0` is the application result.

The captured runtime predates the file-only change disabling Grafana suggested plugin preinstallation and update/usage checks. That later environment change was not rolled out. It does not affect the captured dashboard or target results.

Still pending: successful application metrics, CPU/memory workload observations, controlled alert recovery, Kubernetes capstone CRUD/persistence, and actual Argo CD Git reconciliation. No screenshot or execution output has been fabricated.


This is the earlier capture. See [the completed application monitoring and recovery](../2026-10-07-completed/README.md) for the later verified state.
