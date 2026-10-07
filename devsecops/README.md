# Session 17 — CI/CD and DevSecOps

This session integrates the [TaskBoard application](../final-devops-project/application/), [Dockerfiles](../final-devops-project/docker/), [Kubernetes resources](../final-devops-project/kubernetes/), [Helm chart](../final-devops-project/helm/taskboard/) and [GitHub Actions workflow](../.github/workflows/final-project.yml).

The full security/deployment workflow is manual only; registry publication requires separate explicit confirmation. Automatic PR checks cover tests/build/static configuration and do not substitute for scan or deployment evidence.

## Implemented controls

| Required stage | Implementation and success condition |
|---|---|
| Build and unit test | Backend pytest plus React tests and production build must succeed |
| SAST | Bandit scans backend code; MEDIUM/HIGH findings fail |
| SCA | Trivy scans application dependency files; HIGH/CRITICAL findings fail |
| Secret scan | Gitleaks default rules scan the current repository tree, with redacted reports; any finding fails |
| Docker build | Backend and frontend are built independently and labeled with the source commit |
| Image scan | Trivy scans both images; HIGH/CRITICAL findings fail, including unfixed findings |
| Security gate | Native nonzero scanner exits and GitHub `needs` dependencies block downstream jobs; no suppressed findings |
| Kubernetes deployment | Exact scanned images loaded into a disposable kind cluster, Helm deployment waited on, real UI/API smoke tests |
| Container registry | Explicit, manual `main` dispatch publishes those same artifacts to GHCR only after validation |

The [security policy and reproducible commands](../final-devops-project/security/README.md) describe scanner configuration, exact thresholds, pinned versions, output redaction and negative controls. A scan identifies issues; its exit code plus job dependencies enforce the gate.

## Delivery scope

The instructor's full delivery flow is `build → test → scans → Docker build → image scan → push → Kubernetes deployment`. This PR implements the credential-free path through scanned artifacts and a disposable Kubernetes deployment; that full path remains pending execution. The optional registry publisher is present but does not run on PRs. The live `registry → persistent cluster` demonstration remains pending explicit publication/deployment authorization; no registry push, cloud deployment or fabricated success output is included.

Proposed image names after an authorized publication are:

```text
ghcr.io/jaivardhandrao/devops-term-9-backend:<commit-sha>
ghcr.io/jaivardhandrao/devops-term-9-frontend:<commit-sha>
```

There is no permanent registry token, kubeconfig, cloud key or real database password in the repository. A registry token would be job scoped; a cluster credential is unnecessary for kind. For any later persistent deployment, review identity, target and access separately rather than copying a personal kubeconfig into source control.

## Evidence

Read [dated local security checks](../final-devops-project/security/evidence/README.md), then inspect the actual [GitHub workflow runs](https://github.com/jaivardhandrao/DevOps-Term-9/actions/workflows/final-project.yml). Each run uploads tests, redacted scan reports, negative-control checks and disposable deployment results. Screenshots must come from a completed run, not a mock diagram. A scan failure or an unavailable vulnerability database remains a blocker until fixed and rerun.

## Verified CI prerequisite

This actual [checks job](https://github.com/jaivardhandrao/DevOps-Term-9/actions/runs/37609532257/job/112753122569) passed the unit-test/build/static-configuration prerequisites. It is **not** the DevSecOps scan/deployment run. Actual security outcomes are separately recorded in the linked scanner reports above.

![Actual successful unit-test, build and static-check steps](../evidence/october-7/screenshots/github-actions-job-112753122569.jpg)
