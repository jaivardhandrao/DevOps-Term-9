# DevOps Homework — Term 9

**Jaivardhan D. Rao · 24BCS10117**

Coursework for the current **20 submission topics, sessions 1–21**. The October update extends the previous Linux/Docker/Kubernetes work with storage, troubleshooting, Helm, CI/CD, security, Terraform, monitoring, GitOps and a PostgreSQL-backed TaskBoard capstone.

**Coverage update, 7 October 2026:** actual local practicals, browser screenshots and security reports are added to the merged `main` branch while preserving all 20 submitted README paths. The [evidence checklist](EVIDENCE-CHECKLIST.md) separates completed observations from remaining service-journal, host-port, screenshot, registry and cloud requirements. Code, static validation and mocked tests are not described as live deployment evidence.

## Coursework map

| Session | Topic |
| --- | --- |
| 1 & 2 | [Linux Fundamentals](linux-fundamentals/README.md) |
| 3 | [Shell Scripting](shell-scripting/README.md) |
| 4 | [Networking Fundamentals](networking/README.md) |
| 5 | [Git and GitHub](git-github/README.md) |
| 6 | [Docker Fundamentals](docker-apps/README.md) |
| 7 | [Dockerfiles and Images](multi-stage-build/README.md) |
| 8 | [Docker Networking](docker-networking/README.md) |
| 9 | [Kubernetes Fundamentals](kubernetes-fundamentals/README.md) |
| 10 | [Kubernetes Pods, ReplicaSets and Deployments](kubernetes-core-objects/README.md) |
| 11 | [Kubernetes Networking and Services](kubernetes-services/README.md) |
| 12 | [Kubernetes Ingress, ConfigMaps and Secrets](kubernetes-ingress-configmaps-secrets/README.md) |
| 13 | [Kubernetes Storage, HPA and Probes](kubernetes-storage-hpa-probes/README.md) |
| 14 | [Kubernetes Troubleshooting](kubernetes-troubleshooting/README.md) |
| 15 | [Helm](helm/README.md) |
| 16 | [CI/CD and GitHub Actions](ci-cd/README.md) |
| 17 | [Complete CI/CD and DevSecOps](devsecops/README.md) |
| 18 | [Terraform and Infrastructure as Code](terraform-s3-demo/README.md) |
| 19 | [Cloud and Terraform in Action](cloud-terraform/README.md) |
| 20 | [Monitoring, Observability and GitOps](monitoring-observability-gitops/README.md) |
| 21 | [Final DevOps Project and Troubleshooting](final-devops-project/README.md) |

## Actual verification

- Linux, shell, networking and Git exercises were rerun in disposable containers or repositories. All six Docker apps and the multi-stage app were built and served real HTTP responses; genuine browser screenshots are embedded in their existing READMEs.
- Sessions 9–12 have fresh guarded current-state observers and the original actual strategy/lifecycle/DNS/Ingress transcripts. [October evidence](evidence/october-7/README.md) distinguishes current-state screenshots from earlier failure/recovery observations.
- Session 13 demonstrated PVC persistence and automatic HPA scaling **2 → 5 → 2**. Session 14 exercised all nine troubleshooting categories. Session 15 completed install, upgrades, failure/rollback, uninstall and a healthy review reinstall; its browser image shows the actual Notes app.
- The TaskBoard app has **11 backend and 5 frontend tests**, PostgreSQL CRUD/outage/recovery evidence and desktop/mobile browser screenshots. A local Kubernetes deployment and database replacement preserved its task on the same PVC; [application evidence](final-devops-project/application/evidence/README.md) and [platform evidence](final-devops-project/kubernetes/evidence/2026-10-07/) record their distinct scope.
- Real security scans found and then resolved **44 backend and 42 frontend HIGH package/advisory matches**. Rebuilt local images, application dependencies, Bandit and Gitleaks pass their configured gates; all synthetic negative controls pass. [Before/after reports](final-devops-project/security/evidence/README.md) preserve findings and image IDs. No severity gate was weakened.
- The [full security and disposable deployment run](https://github.com/jaivardhandrao/DevOps-Term-9/actions/runs/37664321492) passed on commit `a218511`: tests, source gates, both AMD64 image scans, migrations, real Helm deployment, API CRUD and HPA metrics checks. The disposable CI cluster was removed; registry publication was skipped.
- Prometheus reports healthy application metrics; a real readiness alert fired during a bounded routing fault and recovered after restoration. Argo reached Synced/Healthy and automatically corrected deliberate configuration drift. The Grafana memory display threshold was corrected to use bytes consistently with the configured request/limit.
- All three Terraform projects pass real provider-schema validation and formatting; **10 mocked tests** pass. No AWS resources were created.

[SUBMISSION.md](SUBMISSION.md) preserves all **20 main README URLs**. The automatic workflow now checks those paths and repository-relative links/images on every main push. PR #4 was merged before this coverage pass; this update does not submit or resubmit a form.

## Local capstone

Start with [TaskBoard application setup](final-devops-project/application/README.md). Its Compose services are isolated under `devops-oct7-capstone`, with the web app published only at `127.0.0.1:18080`. Disposable passwords live in ignored runtime files. The application is a local classroom demo without authentication; do not expose it publicly as a production service.

The original September evidence is retained. New automated runs are explicitly attributed to the agent; they are not described as actions performed personally by the student. Screenshots are labeled by what they actually show.
