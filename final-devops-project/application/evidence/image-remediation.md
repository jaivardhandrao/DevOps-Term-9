# Application image remediation — 7 October 2026

Actual Trivy scans found 44 HIGH OS-package findings in the original Debian backend
image and 42 HIGH OS-package findings in the original Alpine frontend image. Python
application dependency scanning passed. The original reports are retained in
[backend-image-before.json](../../security/evidence/backend-image-before.json) and
[frontend-image-before.json](../../security/evidence/frontend-image-before.json).

The backend Dockerfile now uses `python:3.12-alpine` and upgrades its OS packages before
installing the unchanged pinned Python dependencies. Alpine user/group creation preserves
the original nonroot runtime UID/GID `10001:10001`. The frontend upgrades OS packages as
root during build and returns to runtime user `101:101`. No scanner exclusions were added.

The first build failed on an Alpine repository DNS lookup. The actual failure remains in
[patched-images-build.txt](patched-images-build.txt). A disposable DNS check then resolved
the repository, and the bounded retry completed all three images successfully:
[patched-images-build-retry.txt](patched-images-build-retry.txt).

Validation against the rebuilt images:

| Check | Observed result |
| --- | --- |
| [Backend tests](patched-backend-tests.txt) | 11 passed; one existing Starlette/httpx deprecation warning |
| [PostgreSQL native driver](patched-postgres-read.txt) | New musllinux image connected to the disposable database; migration `0001`, existing demonstration task count `1` |
| [Frontend configuration](patched-nginx-config.txt) | Entrypoint template rendering and `nginx -t` succeeded as the nonroot frontend user |
| [Actual runtime users](patched-nonroot.txt) | Backend `uid=10001 gid=10001`; frontend `uid=101 gid=101`, each verified with `id` inside the rebuilt image |
| [Backend Trivy report](../../security/evidence/backend-image.json) | HIGH/CRITICAL image gate passed with zero findings at those severities |
| [Frontend Trivy report](../../security/evidence/frontend-image.json) | HIGH/CRITICAL image gate passed with zero findings at those severities |

The PostgreSQL check used a temporary Compose container and read only migration metadata
and a row count. The frontend configuration check also used a temporary container.
Existing Compose/Kubernetes application containers were not recreated by this remediation
step, and no registry push or cloud deployment is claimed here. Rebuild and scan results
describe the new local images; the security reports preserve their scanned image IDs.
