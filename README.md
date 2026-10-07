# DevOps Homework — Term 9

**Jaivardhan D. Rao · 24BCS10117**

Coursework for the current **20 submission topics, sessions 1–21**. The October update extends the previous Linux/Docker/Kubernetes work with storage, troubleshooting, Helm, CI/CD, security, Terraform, monitoring, GitOps and a PostgreSQL-backed TaskBoard capstone.

**Draft completion status:** implementations and runbooks are prepared across the current scope. Several practical requirements remain unverified because runtime approval was blocked or live cloud operations were outside this task's authorization. Do not interpret code, expected-output descriptions, schema validation or mocked tests as proof that those deployments ran. [The evidence checklist](EVIDENCE-CHECKLIST.md) records the exact gaps.

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

- The final app has 11 backend and 5 frontend tests, successful container/frontend builds, real PostgreSQL CRUD, database outage/recovery and restart-persistence evidence, plus desktop/mobile browser screenshots. See [application evidence](final-devops-project/application/evidence/README.md).
- Sessions 9–12 have fresh local command transcripts; session 12's invalid Kubernetes label was found by the API server and fixed. [October evidence](evidence/october-7/README.md) separates successful checks from failed attempts and remaining external-address/screenshot requirements.
- All three Terraform configurations pass real provider-schema validation and formatting; **10 mocked tests** pass. No AWS resources were created.
- The Notes Helm chart renders with development and production values. The final application chart also passes lint and rendering.
- The existing capture-runner tests and new invalid-label regression checks pass: **14 tests**. Earlier sandbox-only failures were caused by prohibited `/dev/fd` process substitution; the fake-CLI tests passed when run with that sandbox restriction lifted.
- Local Bandit SAST and Gitleaks secret scans pass, and both reject their synthetic negative controls. Trivy dependency/image scans and the full CI/CD execution remain pending. The [workflow](.github/workflows/final-project.yml) retains its security gates; image publication and external deployment are not claimed.

[SUBMISSION.md](SUBMISSION.md) maps all 20 current form fields to README URLs. This task did not merge a PR or submit the form.

## Local capstone

Start with [TaskBoard application setup](final-devops-project/application/README.md). Its Compose services are isolated under `devops-oct7-capstone`, with the web app published only at `127.0.0.1:18080`. Disposable passwords live in ignored runtime files. The application is a local classroom demo without authentication; do not expose it publicly as a production service.

The original September evidence is retained. New automated runs are explicitly attributed to the agent; they are not described as actions performed personally by the student. Screenshots are labeled by what they actually show.
