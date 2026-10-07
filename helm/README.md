# Session 15 — Helm and the Notes mini-project

This hand-authored [Notes chart](notes-chart/) packages a small Nginx landing page, Service and ConfigMap. The page displays its environment and message so an upgrade or rollback can be verified through HTTP. A checksum annotation rolls Pods when the ConfigMap changes, avoiding stale environment variables and subPath-mounted content.

**Execution status (October 7, 2026): runtime incomplete.** Development and production chart linting passed and templates rendered locally. Live install, upgrades, rollback and uninstall were not executed because automatic approval review blocked local cluster mutation under the earlier read-only scope. The workflow below is prepared, not a claim of completed commands. See [evidence status](evidence/README.md).

## Chart structure

```text
notes-chart/
  Chart.yaml              # package metadata and chart/application versions
  values.yaml             # development defaults, image, Service and resources
  values-prod.yaml        # three replicas and production page values
  templates/
    configmap.yaml        # environment values and HTML
    deployment.yaml       # probes, requests/limits and content checksum
    service.yaml          # forwards to the container's named HTTP port
```

The chart uses release-qualified resource names and release labels so multiple releases can coexist. The Service defaults to ClusterIP; this lab tests it from a Pod and does not allocate a public IP. The “production” values are a values-file exercise, not a production-readiness claim.

## Reproduce the recorded lifecycle

With `KUBECONFIG` pointed at the fresh disposable `devops-oct7` cluster:

```bash
HELM=/path/to/helm python3 helm/run-lab.py
```

The [driver](run-lab.py) uses a dedicated `devops-helm` namespace and workspace-only Helm cache/config/data directories. It explicitly selects `devops-oct7` and refuses a non-local API endpoint. It first practices `helm create` in a scratch directory; the submitted chart stays intentionally small rather than retaining an unused scaffold.

Helm v3.19.0 for Darwin arm64 was downloaded to the workspace (not installed globally), with archive SHA-256 checked against the vendor's `.sha256sum`: `31513e1193da4eb4ae042eb5f98ef9aca7890cfa136f4707c8d4f70e2115bef6`.

## Commands and their purpose

| Command | Purpose and evidence |
|---|---|
| `helm create` | Generate a reference chart scaffold in scratch |
| `helm lint` | Check chart structure/template conventions |
| `helm template` | Render Kubernetes YAML without installing it |
| `helm repo add/update/list` | Add and refresh the official ingress-nginx chart index; no remote chart is installed |
| `helm search repo` | Inspect versions offered by that index |
| `helm install notes ... --wait` | Create the first release and wait for readiness |
| `helm list` | List releases in `devops-helm` |
| `helm status notes` | Read release state and revision |
| `helm get values --all` | Inspect resolved release configuration |
| `helm get manifest` | Inspect exactly which manifests Helm stored |
| `helm upgrade ... -f values-prod.yaml --wait` | Apply production values and verify three replicas plus changed HTTP content |
| second `helm upgrade ... --set image.tag=devops-intentionally-missing` | Deliberately create a failed image rollout and inspect the actual error |
| `helm history notes` | Record revisions and statuses |
| `helm rollback notes 2 --wait` | Restore revision 2 content/image/configuration and verify healthy Pods/HTTP |
| `helm uninstall notes --wait` | Remove the release resources, then inspect remaining state |

## Rollback workflow and observations

```text
Install revision 1 (development)
  -> Upgrade revision 2 (production, 3 replicas)
  -> Verify environment and HTML through the Service
  -> Upgrade revision 3 (intentionally nonexistent image)
  -> Observe ErrImagePull/ImagePullBackOff in Kubernetes
  -> Rollback to revision 2 (creates a new revision)
  -> Verify restored production environment and response
  -> Uninstall
  -> Reinstall a small development release for review
```

A successful `helm upgrade` without `--wait` means the API accepted the manifests; it does not prove the Pods are healthy. The bad-image exercise demonstrates that difference. A rollback creates another history revision; it does not erase the failed revision. `--atomic` can automatically undo a failed waited upgrade, but this exercise performs the rollback explicitly to capture each step.

The service port is independently configurable and forwards to named container port `http` (80), so changing an exposed Service port does not accidentally change Nginx's listener. ConfigMap values carry no secrets. Actual secrets should be supplied separately and never printed through `helm get` or committed in values files.

## Actual evidence

The [static validation record](evidence/static-validation.txt) contains actual Helm version and two successful lint runs. The driver will create `evidence/helm-run.txt` only when it executes; no live Helm lifecycle record or screenshot is currently available. No expected-output screenshot has been fabricated.

References: [instructor mini-project](https://github.com/Nency-Ravaliya/devops-heros/tree/main/session-15-helm/mini-project), [Helm CLI](https://helm.sh/docs/helm/), [rollback command](https://helm.sh/docs/helm/helm_rollback/), [chart template guide](https://helm.sh/docs/chart_template_guide/).
