# Completed application monitoring — October 7, 2026

Captured from the disposable `devops-oct7` cluster, with patched TaskBoard images in `capstone-oct7` and Prometheus/blackbox/Grafana in `monitoring-oct7`. Access used loopback port-forwards only. No notification receiver is configured.

- [Grafana screenshot](grafana.jpg): genuine dedicated-browser capture, with healthy API and database/schema panels. [Original threshold-bug screenshot](grafana-before-threshold-fix.jpg) is retained; the corrected RSS panel uses yellow128MiB / red230.4MiB thresholds.
- [Scrape health](scrape-health.json) and [readiness](readiness.json): both `1`. [CPU](cpu-cores.json), [memory](memory-bytes.json), [request count](request-count.json) and [latency](latency-p95.json) are actual Prometheus query results.
- [Container resource usage](container-resource-usage.txt) and [backend logs](backend-logs.txt) supplement process metrics. Tracing is documented, not deployed.
- [Firing alert](alerts-firing.json): deliberately unmatched backend Service selector produced HTTP502, empty endpoints, probe0 and `TaskBoardNotReady` firing. An existing TCP scrape connection kept `up=1`; no second alert is claimed for this run.
- [Recovery](alerts-recovered.json): correct selector restored, HTTP200, up1/probe1, no firing alerts, original Argo automatic-sync policy restored.
- [Grafana health](grafana-health.json), [provisioned dashboard](grafana-dashboard.json) and [Prometheus targets](prometheus-targets.json) are raw API evidence. “No data” in the active-alert table corresponds to an empty firing-alert result, not a failed scrape.

The [earlier unavailable-target capture](../2026-10-07/README.md) remains unchanged as historical evidence. The [GitOps demo](../../../gitops/README.md) separately proves reconciliation and self-healing. The first selector test expected both alerts; it failed that overly broad assertion, cleaned up, and the corrected test above verified the observed readiness alert and recovery.
