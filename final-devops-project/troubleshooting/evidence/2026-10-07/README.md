# Actual final troubleshooting checks — October 7, 2026

All actions targeted only `devops-oct7` / `capstone-oct7`.

1. **Service selector mismatch:** [healthy baseline](selector-healthy-before.json), [failure](selector-fault.json) and [recovery](selector-recovered.json). The wrong component selector removed ready endpoints; the frontend returned502 and `TaskBoardNotReady` fired with probe0. Prometheus’s established metrics TCP connection survived, so up remained1. The first test’s expectation of two firing alerts was therefore incorrect and was corrected. The final test restored HTTP200, up1/probe1 and zero firing alerts. Argo automation was temporarily paused for the alert hold period and its exact original policy was restored in a `finally` block.
2. **Missing image:** [Pod failure](image-fault-before.json), [diagnostic events](image-fault-events.txt) and [corrected Pod](image-fault-recovered.json). A separate disposable Deployment used an absent tag with `imagePullPolicy: Never` and reached `ErrImageNeverPull`. Pointing it at the loaded local image completed rollout. The extra Deployment was then deleted.

No PVC or database data was deleted by these fault tests. The [separate persistence test](../../../kubernetes/evidence/2026-10-07/persistence.json) proved a task survived PostgreSQL Pod replacement and cleaned up its temporary record.
