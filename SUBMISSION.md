# Section A: current submission link map

**Name:** Jaivardhan D. Rao · **Enrollment:** 24BCS10117

The [current Section A form](https://docs.google.com/forms/d/e/1FAIpQLSflx5OGn4fnKascC379yPBO1cgQLFSOtbcKLmzNRSqh6ifPQg/viewform) was inspected on 7 October 2026. It requires **20 README GitHub links**: sessions 1–2 combined, then each session 3–21. This replaces the September 11-field map. Paste the README URL, not a repository homepage or PR link.

The **20 `main` URLs below are the permanent submission targets**. PR #4 has been merged, so these paths no longer depend on its draft branch. The October 7 coverage update preserves every URL and validates linked repository assets. No form is submitted or resubmitted by this update. Review [the evidence checklist](EVIDENCE-CHECKLIST.md) for the remaining practical and screenshot gaps.

| Session | Required topic | Submitted README on main |
| --- | --- | --- |
| 1 & 2 | Linux Fundamentals | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/linux-fundamentals/README.md) |
| 3 | Shell Scripting | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/shell-scripting/README.md) |
| 4 | Networking Fundamentals | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/networking/README.md) |
| 5 | Git and GitHub | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/git-github/README.md) |
| 6 | Docker Fundamentals | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/docker-apps/README.md) |
| 7 | Dockerfiles and Images | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/multi-stage-build/README.md) |
| 8 | Docker Networking | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/docker-networking/README.md) |
| 9 | Kubernetes Fundamentals | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/kubernetes-fundamentals/README.md) |
| 10 | Kubernetes Pods, ReplicaSets and Deployments | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/kubernetes-core-objects/README.md) |
| 11 | Kubernetes Networking and Services | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/kubernetes-services/README.md) |
| 12 | Kubernetes Ingress, ConfigMaps and Secrets | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/kubernetes-ingress-configmaps-secrets/README.md) |
| 13 | Kubernetes Storage, HPA and Probes | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/kubernetes-storage-hpa-probes/README.md) |
| 14 | Kubernetes Troubleshooting | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/kubernetes-troubleshooting/README.md) |
| 15 | Helm | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/helm/README.md) |
| 16 | CI/CD and GitHub Actions | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/ci-cd/README.md) |
| 17 | Complete CI/CD and DevSecOps | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/devsecops/README.md) |
| 18 | Terraform and Infrastructure as Code | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/terraform-s3-demo/README.md) |
| 19 | Cloud and Terraform in Action | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/cloud-terraform/README.md) |
| 20 | Monitoring, Observability and GitOps | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/monitoring-observability-gitops/README.md) |
| 21 | Final DevOps Project and Troubleshooting | [README](https://github.com/jaivardhandrao/DevOps-Term-9/blob/main/final-devops-project/README.md) |

Session 18 links the required [five AWS service research READMEs](aws-services/). Sessions 16–17 reuse the final application and the executable root workflow; GitHub does not execute workflows nested inside a subfolder.

The URL checker verifies all 20 paths and all relative Markdown links/images. After a push, its optional remote check also verifies public GitHub pages and compares README bytes at the pushed commit:

```bash
python3 scripts/check-submission-links.py
python3 scripts/check-submission-links.py --remote-ref <full-pushed-commit-sha>
```

Future evidence additions should keep these README paths stable. Historical evidence can link immutable commits without changing the submitted `main` URLs.

## Source authority

The [homework document](https://docs.google.com/document/d/1cjXFYf2Thm8cBEN-0C48B-v02cj3jGLd47lcO18prHE/edit) was modified on 4 October 2026 and explicitly adds sessions 13–21. The form confirms those fields. The instructor's `session21-python/README.md` describes the final TaskBoard capstone, not merely a Python lesson. Neither inspected homework text nor form provides the deadline's exact time or time zone.
