# Security controls and evidence

This is a classroom application. The automated checks below reduce specific risks; they do not establish production readiness. The application is intended for a local, isolated demonstration until authentication, authorization, TLS, backups and operational ownership are added.

## Four blocking gates

The executable workflow is [`../../.github/workflows/final-project.yml`](../../.github/workflows/final-project.yml). It uses `needs` dependencies, with no `continue-on-error` on any gate. The full workflow is manual dispatch only pending accepted execution approval. The separate automatic `assignment-checks.yml` workflow runs only unit tests, frontend builds and static Kubernetes/Helm validation.

| Layer | Pinned tool | Scope | Blocking rule |
|---|---|---|---|
| SAST | Bandit 1.9.4 | Backend application Python | Any MEDIUM/HIGH severity result; all confidence levels |
| SCA | Trivy 0.75.0 | Application dependency manifests/lockfiles | Any HIGH/CRITICAL vulnerability, including unfixed findings |
| Secrets | Gitleaks 8.30.1 | Entire checked-out repository directory | Any detected secret; output fully redacted |
| Container | Trivy 0.75.0 | Both final Docker images, OS and language packages | Any HIGH/CRITICAL vulnerability, including unfixed findings |

There are no CVE exceptions, secret allowlists, `--ignore-unfixed` flags or scan-error fallbacks. A database-download failure is a failed scan, not a clean result. The secret scan checks the current tree, not historic commits; credentials found in history would still require revocation and a separate history review.

Bandit detects Python coding patterns and does not cover JavaScript source; dependency and container scans include the frontend. Infrastructure configuration validation is documented with the Terraform and Kubernetes work, separately from these four gates.

GitHub Actions dependencies are pinned to verified commit hashes. Scanner binaries are pinned to versions and checked against the publisher's SHA256 checksum file. Dependency vulnerability databases remain live, so a previously passing commit can fail when new advisories appear. These release checksums protect download integrity; they do not replace a separately trusted signature verification policy.

## Reproduce

From the repository root, install Bandit in an isolated Python environment and put the pinned `trivy` and `gitleaks` binaries on `PATH`. The Linux CI bootstrap is `bash final-devops-project/security/install-ci-tools.sh security /tmp/taskboard-ci-bin`.

```bash
bandit -r final-devops-project/application/backend/app --severity-level medium
trivy fs --scanners vuln --severity HIGH,CRITICAL --exit-code 1 final-devops-project/application
gitleaks dir . --config final-devops-project/security/gitleaks.toml --redact=100
docker build --pull -f final-devops-project/docker/backend.Dockerfile -t taskboard-backend:local final-devops-project
docker build --pull -f final-devops-project/docker/frontend.Dockerfile -t taskboard-frontend:local final-devops-project
trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 taskboard-backend:local
trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 taskboard-frontend:local
bash final-devops-project/security/test-gates.sh
```

`test-gates.sh` generates disposable weak-crypto, synthetic-secret and vulnerable dependency fixtures outside the repository. It requires each real scanner to reject its fixture with exit 1. It also re-evaluates the actual vulnerable Trivy report. The latter checks report severity handling and is explicitly **not** an image scan; both real images are configured for scanning in the full workflow. `bash final-devops-project/security/test-gates.sh local` runs only the offline SAST/secret controls and explicitly reports that Trivy controls were not executed.

## Secrets and publication

CI has read-only repository access. It generates a random, temporary database password in a file, passes it into a Secret in its disposable kind cluster, and never prints it. The app consumes the password through a mounted file. Reports never dump Secret resources or environment variables.

The publication job has `packages: write` only when explicitly dispatched on `main` with `publish_images=true` and confirmation `PUBLISH TO GHCR`. Its temporary `GITHUB_TOKEN` is passed through standard input to Docker login. PR and ordinary push events never publish images, and no job deploys to AWS or an existing cluster. Images are tagged with the commit SHA; the publication job loads the already scanned image artifacts instead of rebuilding a different image.

## Observed results

See [`evidence/README.md`](evidence/README.md) for dated results. Workflow artifacts will contain scanner JSON, negative-control output and deployment checks when a GitHub run actually executes. A workflow file or expected command is not evidence that a scan passed.
