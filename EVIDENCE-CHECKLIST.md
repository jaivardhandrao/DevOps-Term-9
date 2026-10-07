# Coursework evidence and completion checklist

**Status recorded: 7 October 2026. This is a draft implementation, not a claim that every practical requirement is complete.**

The current homework and Section A form have **20 topics covering sessions 1–21**. Sessions 1–2 share one field. The [submission map](SUBMISSION.md) provides all 20 README links. Earlier September work covered only 11 fields; that draft was not submitted during this task.

## Requirement-by-requirement status

| Sessions | Supplied work and actual evidence | Remaining evidence or work |
| --- | --- | --- |
| 1–2 | Existing Linux README, commands and prior coursework retained | Prior artifacts were inspected, not rerun in October; review against the current homework before submission |
| 3 | Existing shell scripts and README retained | No new execution claimed |
| 4 | Existing networking work retained | No new network exercise claimed |
| 5 | Existing Git/GitHub work retained | No new instructor submission claimed |
| 6 | Existing Docker application work retained | No fresh rerun of this older session |
| 7 | Existing multi-stage image work retained | No fresh rerun of this older session |
| 8 | Existing Docker networking work retained | No fresh rerun of this older session |
| 9 | Ready node, CoreDNS, namespace/default ServiceAccount and healthy client observed on a new isolated Minikube profile | New native Terminal screenshot if required; earlier actual screenshot retained |
| 10 | ReplicaSet replacement, rolling update/rollback, blue/green, canary, recreate and all 12 lifecycle/probe fixtures observed in actual transcripts | Required fresh screenshots; do not substitute expected-output text |
| 11 | ClusterIP, NodePort, ExternalName, headless DNS, internal LoadBalancer routing and broken-selector recovery observed; comparison/FQDN/CoreDNS docs added | External LoadBalancer address remains pending; fresh screenshots |
| 12 | HTTP Ingress frontend/API routes, ConfigMap restart, mounted Secret presence without disclosure, broken-route failure and recovery observed; invalid frontend label fixed | TLS demonstration and required screenshots remain pending |
| 13 | Storage documentation, original HTTP mini-project, PVC/probes/HPA and bounded load driver; four real local HTTP routes verified | Live PVC retention, CPU/load, HPA scale-out/recovery, probes and screenshots blocked before workloads were created |
| 14 | Nine issue categories, fourteen broken/fixed fixture files, diagnosis commands and Nginx mini-project | Live failure/root-cause/fix observations and screenshots pending |
| 15 | Notes chart, production values, command reference and install/upgrade/rollback driver; lint/render, local `helm create`, port/escaping/isolation/checksum checks pass | Actual install, two upgrades, rollback/history, repository/search and uninstall evidence pending |
| 16 | Application Dockerfiles and GitHub Actions workflow supplied | Successful full pipeline, image publication and deployment evidence pending |
| 17 | SAST, SCA, secret/image scanning and blocking gates supplied. Actual Bandit and Gitleaks scans pass and reject synthetic negative controls | Trivy dependency/image scans, their controls and full deployment pipeline evidence pending; no all-scans-clean claim |
| 18 | Required S3 Terraform layout, five AWS service research READMEs; real provider validation/formatting and two mocked tests pass | Actual AWS plan/apply/show/output/destroy and screenshots require separate cloud authorization |
| 19 | VPC/subnet/routes/security group/EC2/S3 configuration and architecture; real provider validation/formatting and four mocked tests pass | Actual AWS lifecycle, application access and cleanup evidence pending |
| 20 | Prometheus/Grafana/blackbox configs, dashboard, alert rules, logs/traces explanation and GitOps setup; three monitoring Pods ready, Grafana healthy with seven panels | App target is absent and availability alerts fire; capture healthy application metrics, CPU/memory behavior, alert recovery and actual GitOps reconciliation |
| 21 | Responsive React/FastAPI/PostgreSQL app; 11 backend + 5 frontend tests; images build; actual CRUD, outage/recovery and persisted task after restart; desktop/mobile screenshots. Helm renders; EKS provider validation and four mocked tests pass | Kubernetes app deployment/PVC recovery/HPA/Ingress, full security CI, registry push, cloud deployment, GitOps and platform fault/fix screenshots pending |

## Evidence locations

- [October Kubernetes transcripts](evidence/october-7/README.md) identify successful runs and retain failed attempts. They are actual command output from agent-run checks, not native Terminal screenshots.
- [Application tests, HTTP/persistence logs and screenshots](final-devops-project/application/evidence/README.md).
- [S3 provider/mock results](terraform-s3-demo/evidence/local-validation.txt), [EC2/VPC/S3 provider/mock results](cloud-terraform/evidence/local-validation.txt), [EKS provider/mock results](final-devops-project/terraform/evidence/local-validation.txt): **10 mocked Terraform tests total**, not cloud deployment evidence.
- [Monitoring runtime evidence](final-devops-project/monitoring/evidence/2026-10-07/README.md) explicitly shows the missing application target and firing alerts.
- Existing capture-runner tests and label regression tests: **14 passed**. [Chart probe check](scripts/check-chart-probes.py) verifies the frontend probe stays independent of backend health.
- [Security evidence inventory](final-devops-project/security/evidence/README.md) records passing Bandit/Gitleaks scans and negative controls, separately from pending Trivy scans.

## Execution boundaries and next steps

The original checkout under `Desktop/SST_CU/Term 9/devops/devops-homework` was left intact. New checks used an isolated `devops-oct7` Minikube profile and `devops-oct7-capstone` Compose project. The host's current Kubernetes context was not changed. Generated passwords, runtime files and Terraform state are ignored; no credentials are intentionally included in evidence.

Automatic approval review rejected some advanced Kubernetes, capstone deployment and security-scan commands because it applied the task's original read-only instruction and did not accept later delegated authorization. Those rejected commands were not rerouted or treated as successes. The full security/deployment workflow remains manual while that authorization is unresolved.

After authorization is resolved, run the supplied bounded local drivers and full pipeline, inspect real results, fix any failures and capture missing evidence. AWS work is a separate pending step because paid provisioning and access changes were outside this task's scope. EKS also requires a reviewed operator identity, private API access, appropriate storage/controller prerequisites and cleanup verification.

No form submission, PR merge, live AWS provisioning or notifications to others were performed. A draft PR allows review of the code and these explicit gaps; merging it does not itself complete the missing demonstrations.
