# Workflow location

GitHub discovers executable workflows only in the repository-root `.github/workflows/` directory. The runnable final-project workflow is therefore [`.github/workflows/final-project.yml`](../../../.github/workflows/final-project.yml).

This requested capstone directory documents that mapping instead of duplicating inactive YAML. The same workflow covers sessions 16, 17 and 21: tests/builds, four security gates, scanned image artifacts, disposable Kubernetes/Helm deployment and an explicitly gated optional registry publication. See [CI/CD](../../../ci-cd/README.md) and [DevSecOps](../../../devsecops/README.md) for the stage-by-stage explanation and evidence status.

The full workflow is manual dispatch only; the optional registry publisher requires separate explicit confirmation. The separate root `assignment-checks.yml` runs automatic PR unit tests, frontend builds and static Kubernetes/Helm checks; it performs no scan, cluster write, registry push or cloud action.
