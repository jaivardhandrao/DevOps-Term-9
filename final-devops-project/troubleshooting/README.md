# Final troubleshooting challenge

Perform this only in the dedicated coursework namespace/context, after capturing healthy CRUD and monitoring output. The following two independent faults exercise resource inspection, diagnosis, correction and verification. Both were executed on October 7; [saved runtime evidence](evidence/2026-10-07/README.md) records failure, correction and recovery.

## Fault 1: Service points to no Pods

Symptoms: frontend API requests return a gateway failure, backend EndpointSlices lose ready addresses, `TaskBoardNotReady` fires. `TaskBoardUnavailable` fires only if the metrics scrape also fails: an existing keep-alive TCP connection can survive a Service-selector change and leave `up=1`.

```sh
# If Argo owns this app, temporarily pause its automatic repair during the drill.
# Save the existing automated policy and restore it afterward.
kubectl --context devops-oct7 -n monitoring-oct7 patch application taskboard --type=merge \
  -p '{"spec":{"syncPolicy":{"automated":{"enabled":false}}}}'
kubectl --context devops-oct7 -n capstone-oct7 get service backend -o yaml
kubectl --context devops-oct7 -n capstone-oct7 patch service backend --type=merge \
  -p '{"spec":{"selector":{"app.kubernetes.io/component":"deliberately-missing"}}}'
kubectl --context devops-oct7 -n capstone-oct7 get endpointslice -l kubernetes.io/service-name=backend
kubectl --context devops-oct7 -n capstone-oct7 get pods --show-labels
curl -sS http://127.0.0.1:18081/ready
# After the 15-second alert duration and a scrape/evaluation interval:
curl -fsS http://127.0.0.1:19090/api/v1/alerts
# Fix the selector; preserve all other fields.
kubectl --context devops-oct7 -n capstone-oct7 patch service backend --type=merge \
  -p '{"spec":{"selector":{"app.kubernetes.io/component":"backend"}}}'
curl -fsS http://127.0.0.1:18081/ready
# The supplied Application starts enabled=true; restore its original policy.
kubectl --context devops-oct7 -n monitoring-oct7 patch application taskboard --type=merge \
  -p '{"spec":{"syncPolicy":{"automated":{"enabled":true}}}}'
```

Root cause: the Service selector did not match the Deployment's Pod labels. DNS still resolved the Service, and backend Pods remained alive; DNS and process restarts would not fix the missing endpoints. Validate restored endpoints, readiness, CRUD and cleared alerts.

## Fault 2: Deployment references an unavailable local image

The image is intentionally missing and pullPolicy is Never, so this test produces `ErrImageNeverPull` without contacting a registry or altering the healthy application.

```sh
kubectl --context devops-oct7 -n capstone-oct7 create deployment image-fault --image=taskboard-frontend:deliberately-missing
kubectl --context devops-oct7 -n capstone-oct7 patch deployment image-fault --type=strategic \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"taskboard-frontend","imagePullPolicy":"Never"}]}}}}'
kubectl --context devops-oct7 -n capstone-oct7 get pods -l app=image-fault
kubectl --context devops-oct7 -n capstone-oct7 describe pods -l app=image-fault
kubectl --context devops-oct7 -n capstone-oct7 set image deployment/image-fault taskboard-frontend=taskboard-frontend:local
kubectl --context devops-oct7 -n capstone-oct7 rollout status deployment/image-fault --timeout=120s
kubectl --context devops-oct7 -n capstone-oct7 get pods -l app=image-fault
kubectl --context devops-oct7 -n capstone-oct7 delete deployment image-fault
```

Root cause: the tag is absent from the node's image store. `Never` prohibits a registry fallback. Fixing the tag to the already loaded image starts the container. A cluster using registry pull policy instead may report `ErrImagePull` then `ImagePullBackOff`; do not label this local test as that different condition.

## What to retain

Save timestamps, initial healthy state, the failing HTTP/status/events, investigation commands, root-cause explanation, corrective change, recovered readiness/CRUD and alert state. Never capture Secret values or database connection URLs. Logs and screenshots must come from actual runs.

## Boundaries and cleanup

The API uses a persistent PostgreSQL PVC. Neither exercise deletes database data. Undo a Service-selector fault immediately after collecting evidence, including when interrupted. Delete the extra image-fault Deployment. Session 14 separately covers the broader Kubernetes troubleshooting catalogue.


The selector drill must pause only this Application’s automated sync first; otherwise self-healing can repair the selector before the alert’s 15-second hold period. Always restore both the original Service selector and the original automated-sync policy, including on failure. The executed drill used a `finally` cleanup block. This is separate from the [GitOps drift test](../gitops/evidence/2026-10-07/drift-self-heal.json), which deliberately left self-healing enabled.
