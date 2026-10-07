# Security and workflow validation — 7 October 2026

Evidence is separated into observed checks and pending execution. No security scan success is inferred from configuration alone.

| Check | Observed result |
|---|---|
| `actionlint .github/workflows/*.yml` | Exit 0; no workflow or shell diagnostics |
| `bash -n final-devops-project/security/install-ci-tools.sh final-devops-project/security/test-gates.sh` | Exit 0 |
| `python3 -m py_compile final-devops-project/security/smoke-deployment.py` | Exit 0 |
| Trivy release archive | Version 0.75.0; macOS ARM64 archive SHA256 matched publisher checksum before extraction |
| Bandit installation | Version 1.9.4 installed in an isolated temporary environment |
| Bandit SAST | Exit 0; 155 application lines scanned, zero findings, zero errors; [JSON report](sast.json) |
| Gitleaks current-tree scan | Exit 0; no leaks found; [redacted JSON report](secrets.json) |
| Trivy SCA | Specifically blocked before execution; no report exists |
| Trivy container scans | Never attempted; no image vulnerability result is claimed |
| Deliberate failing gate examples | SAST and secret negative controls both exit 1 as required; [observed output](local-negative-controls.txt). Trivy controls not attempted |
| Automatic tests/static checks | Initial PR runs failed on GNU `mktemp` portability; fixed with an explicit X template. All 14 local fake-CLI/label tests now pass; updated GitHub run pending |
| Full security/deployment pipeline | Manual dispatch only; scans/deployment remain pending execution approval |
| GHCR publication | Not performed; intentionally requires explicit manual authorization |
| Persistent/cloud Kubernetes deployment | Not performed by this workflow |

The Trivy dependency scan was not executed during this validation attempt because execution approval was unavailable; the last retry was cancelled without starting a scanner process. No empty or fabricated report has been substituted. The workflow still fails closed: scanner errors or blocked findings prevent images from reaching the deployment job.

## Scan execution boundaries

Only the Trivy **filesystem dependency scan** was explicitly rejected by execution review. It would download public vulnerability metadata into `/tmp/devops-ci-tools/trivy-cache`, read `final-devops-project/application`, and write `evidence/sca.json`. The minimum outstanding approval for that check is those three actions; it requires no cloud credentials, deployment or registry publication.

Container scans and the Trivy negative controls were not attempted after that rejection. They are pending, not separately reported as rejected. Independent offline Bandit and Gitleaks scans subsequently completed, and the `local` negative-control mode exercised only those two scanners. The full CI workflow remains manual; the PR workflow contains no scanners or deployment action.

## Verified dependency pins

The following tag resolutions were read from the publishers' public Git repositories while authoring the workflow:

| Action tag | Commit used |
|---|---|
| `actions/checkout` v4 | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/setup-python` v5 | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/setup-node` v4 | `49933ea5288caeca8642d1e84afbd3f7d6820020` |
| `actions/upload-artifact` v4 | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| `actions/download-artifact` v4 | `d3f86a106a0bac45b974a628896c90dbdf5c8093` |

Public release metadata was read for [Trivy 0.75.0](https://github.com/aquasecurity/trivy/releases/tag/v0.75.0), [Gitleaks 8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1), [kind 0.33.0](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0), [Helm 4.3.0](https://github.com/helm/helm/releases/tag/v4.3.0) and [Bandit 1.9.4](https://pypi.org/project/bandit/1.9.4/). kind's Kubernetes 1.34.11 node image digest is pinned to the image listed in that kind release.

## Record the next real run

Link the actual GitHub run and its commit, record each job's status, and attach a screenshot captured from that run. Download and inspect the `source-security-*`, `image-*` and `disposable-deployment-*` artifacts before marking the scans and CD complete. Resolve findings by changing vulnerable dependencies/code/images and rerunning; do not reduce severity thresholds to make the run green.
