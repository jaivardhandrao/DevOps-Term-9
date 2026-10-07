# Actual full GitHub pipeline — run 37664321492

[GitHub run](https://github.com/jaivardhandrao/DevOps-Term-9/actions/runs/37664321492), source commit `a21851154ac1bf984ab7c7a0304073a19faac27d`, manual dispatch on `main`, 7 October 2026. The run concluded **success**: five executed jobs passed and the optional GHCR publisher was **skipped**. [API job record](run.json).

## Original run artifacts

- [SAST report](sast.json), [dependency report](sca.json), [redacted secret report](secrets.json): gates passed.
- [Backend AMD64 image report](backend-scan.json) and [frontend AMD64 image report](frontend-scan.json): zero HIGH/CRITICAL findings, including unfixed vulnerabilities in the gate.
- [Negative controls](negative-controls.txt): the actual scanners rejected the intended unsafe fixtures; reports confirmed the expected rule/package.
- [API/UI smoke checks](smoke.txt): frontend HTML, reverse proxy, liveness, database readiness, metrics, create/list/read/update/delete/statistics, invalid-input rejection and deletion cleanup all passed.
- [Helm release](helm.txt): taskboard revision 1 deployed.
- [Resources](resources.txt): backend/frontend/PostgreSQL ready, database PVC bound, migration Job completed. The migration Pod recorded one startup retry before completing.
- [HPA](hpa.txt): CPU 4% of requested resources against the 70% target, one replica. [Pod metrics](pod-metrics.txt) are actual metrics-server results. This verifies metrics availability, not a load-induced scale-up.

The deployment job's cleanup step succeeded, deleting its disposable kind cluster. No registry push, AWS resource, persistent cluster, or live production deployment was involved.

## Provenance

Reports and text outputs were downloaded from this run's actual artifacts. [Provenance](provenance.json) records the source commit and raw/published SHA256 hashes. Source-security and frontend reports are byte-for-byte originals. The backend report omits only the verified public CPython signing-key fingerprint from Docker metadata, matching the documented local-report treatment; all CVE/package results and image identifiers are unchanged. No scanner rule exclusion was added. Raw originals and image archives stay in the local temporary download directory, not this repository.
