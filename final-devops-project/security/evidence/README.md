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
| Trivy SCA | Exit 0; runtime Python (21), test Python (8), and npm including development dependencies (43) have zero HIGH/CRITICAL findings; [JSON](sca.json) |
| Trivy backend image | Exit 0 after remediation; 38 OS and 22 Python packages, zero HIGH/CRITICAL findings; [JSON](backend-image.json) |
| Trivy frontend image | Exit 0 after remediation; 70 OS packages, zero HIGH/CRITICAL findings; [JSON](frontend-image.json) |
| Deliberate failing gate examples | All controls passed: Bandit finding exit 1, Gitleaks/Trivy finding exit 42, expected rule/package verified in JSON; [actual output](negative-controls.txt) |
| Automatic tests/static checks | Initial PR runs failed on GNU `mktemp` portability; fixed with an explicit X template. [GitHub run 37609532257](https://github.com/jaivardhandrao/DevOps-Term-9/actions/runs/37609532257) passed on commit `93c26a1`: 14 regression tests, backend/frontend tests, frontend build, Kubernetes references and Helm rendering/probe/order checks |
| Full security/deployment pipeline | [Run 37664321492](github-run-37664321492/README.md) **success** on `a218511`: five executed jobs passed; registry publisher skipped. Actual scanner and deployment artifacts preserved |
| GHCR publication | Not performed; intentionally requires explicit manual authorization |
| Persistent/cloud Kubernetes deployment | Not performed by this workflow |

## Image findings and remediation

The first actual image gates failed. Their findings are retained in the before reports:

| Image | Before remediation | Remediation | After remediation |
|---|---|---|---|
| Backend | [44 HIGH package/advisory matches, 8 distinct CVEs](backend-image-before.json), Debian 13.7; no Python findings | Compatible Python 3.12 Alpine base, OS package updates, retained UID/GID 10001, rebuild and application tests | [Zero HIGH/CRITICAL matches](backend-image.json); Alpine 3.24.2, 38 OS + 22 Python packages |
| Frontend | [42 HIGH package/advisory matches, 30 distinct CVEs](frontend-image-before.json), including curl/OpenSSL/expat | OS package updates as build-time root, restored runtime UID 101, rebuild and Nginx validation | [Zero HIGH/CRITICAL matches](frontend-image.json); 70 OS packages |

Actual scanned image IDs:

- Backend: `sha256:872f422299f6cdce80a5a2e74d0bc89243d6c5719527b9c9ebac2838afb39af0`
- Frontend: `sha256:7026b798efbe9b09bb301a97f208c355534280f7f9884a8ce558e07acc298897`

The frontend report retains the base image's Alpine 3.23.4 OS metadata while listing the upgraded package versions. No CVE was excluded, no severity threshold was reduced, and unfixed findings remain blocking. These are local ARM64 image results; the GitHub runner independently builds/scans AMD64 images.

## Execution and evidence limits

The dependency/image scans and full negative controls actually ran on 7 October 2026 under the later coverage authorization. The earlier execution block is resolved for these local checks. The negative controls use distinct finding exit codes and parse the intended findings, so operational errors cannot be mistaken for detections.

The published backend image reports omit **only** the public CPython signing-key fingerprint from Docker image metadata. Gitleaks flagged that public fingerprint as a generic key; its value was verified against the [official Python Dockerfile](https://raw.githubusercontent.com/docker-library/python/master/3.12/alpine3.24/Dockerfile). No secret-rule exception was added. CVE results, packages and image IDs are unchanged; [report provenance and original/published hashes](report-provenance.json) document this precise sanitization. Raw originals remain in the local temporary scanner workspace. Frontend/SCA JSON reports are unmodified scanner output.

No native Terminal screenshot is claimed. Existing genuine browser screenshots in sessions 16/17 show the successful tests/static-checks workflow. The full GitHub security/CD run is now separately verified below; its screenshot captions identify the exact run. Registry publication, cloud provisioning and persistent-cluster deployment have not been performed.

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

## Verified full GitHub run

[Run 37664321492](github-run-37664321492/README.md) independently built and scanned the AMD64 images, then deployed those exact artifacts into a new kind cluster. Helm/migrations, frontend/API checks and HPA metrics passed. Cleanup deleted the cluster. The publisher was skipped because publication was disabled. The preserved run artifacts and API job record establish what executed; local ARM64 scans alone were not used as proof of this run.
