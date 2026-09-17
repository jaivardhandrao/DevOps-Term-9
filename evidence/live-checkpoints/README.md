# Actual local Kubernetes evidence

**Jaivardhan D. Rao · 24BCS10117 · 17 September 2026**

## Fundamentals

![Student Terminal screenshot: node and client Pod ready](01-fundamentals.png)

[Original transcript from the resumed run](01-fundamentals.txt)

The student supplied this original screenshot after running the lab on local Minikube
profile `devops-evidence-20260917-210128`. The node is `Ready`, the namespace exists, the
default ServiceAccount exists, and the `dns-client` Pod reached `Ready`. The transcript also
records the successful CoreDNS rollout wait. This confirms the startup-race correction.

At the screenshot checkpoint, macOS reported that two interactive screen captures cannot
run at once. The lab stopped there, before session 10. The screenshot above was supplied
separately by the student; the runner did not save it automatically. Session 10, 11, and 12
live screenshots remain pending.

The runner now pauses after a failed or cancelled screenshot attempt. Close the other picker
with Escape and press Enter to retry, or paste the full path of a manually saved PNG without
surrounding quotes. It copies that file into the attempt folder before continuing. Invalid
paths and non-PNG files leave the checkpoint paused; Ctrl-C stops the run.
