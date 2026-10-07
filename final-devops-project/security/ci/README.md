# Disposable CI metrics provider

`metrics-server-v0.9.0.yaml` is the unmodified [official metrics-server v0.9.0 release manifest](https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.9.0/components.yaml), downloaded on 7 October 2026.

SHA256: `1cec29a5267809306a2c6ec74a3e449abbb705b4a8beed0c8a1963910f72c79b`

The full manual workflow installs it only in the fresh `kind-taskboard-ci` cluster. It adds `--kubelet-insecure-tls` there because kind's disposable kubelet certificate is self-signed. This is a local test accommodation and is not a setting for a persistent or production cluster. The entire cluster is deleted after the job.

CI waits for the metrics API, then verifies that the backend HPA reports `ScalingActive` and captures `kubectl top pods`. That proves availability of resource metrics, not a load-induced scale-up. Actual load/scaling demonstrations remain separate coursework evidence.

Upstream project: [kubernetes-sigs/metrics-server](https://github.com/kubernetes-sigs/metrics-server), Apache-2.0 licensed.
