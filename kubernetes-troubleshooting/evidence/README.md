# Session 14 evidence status

All fourteen broken/fixed JSON fixtures parsed and the driver compiled during preparation. The later explicitly authorized live runs now provide the practical evidence:

- [troubleshooting-run.txt](troubleshooting-run.txt): CrashLoopBackOff, ErrImagePull, ImagePullBackOff, Pending, ContainerCreating/FailedMount, CreateContainerConfigError and failed DNS, with their fixes. The missing image tag was actually reported `not found`, independently of earlier transient Docker DNS failures.
- [troubleshooting-tail-run.txt](troubleshooting-tail-run.txt): focused continuation after correcting an actual startup race; loopback-only binding blocks remote Pod HTTP, binding to all interfaces fixes it, and the broken Service selector is diagnosed and repaired with an HTTP response.

The initial network control request failed because the process had not begun listening despite the Pod appearing Ready. Both network manifests now include an exec startup probe. The initial failure remains in the first record; the successful continuation is not presented as a clean first run.

Reproduce on a fresh disposable namespace after Session 13 with `python3 kubernetes-storage-hpa-probes/run-lab.py troubleshooting`. The `troubleshooting-tail` option replaces only the named network Pod and reruns the final network/Service cases when resuming that stage.

The corrected app and Pods remain for review. Native Terminal screenshots are still blocked by CUA's explicit refusal to access `com.apple.Terminal`; no alternate native automation or artificial log image was used.
