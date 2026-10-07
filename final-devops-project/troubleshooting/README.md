# Final troubleshooting challenge

Perform this only in the dedicated coursework namespace/context, after capturing healthy CRUD and monitoring output. The following two independent faults exercise resource inspection, diagnosis, correction and verification. These are reproducible instructions; completion is established only by saved runtime evidence.

## Fault 1: Service points to no Pods

Symptoms: frontend API requests return a gateway failure, backend EndpointSlices lose ready addresses, Prometheus `TaskBoardUnavailable` and `TaskBoardNotReady` eventually fire.

```sh
kubectl --context devops-oct7 -n capstone-oct7 get service backend -o yaml
kubectl --context devops-oct7 -n capstone-oct7 patch service backend --type=merge \
  -p '{"spec":{"selector":{"app.kubernetes.io/component":"deliberately-missing"}}}'
kubectl --context devops-oct7 -n capstone-oct7 get endpointslice -l kubernetes.io/service-name=backend
kubectl --context devops-oct7 -n capstone-oct7 get pods --show-labels
curl -sS http://127.0.0.1:18080/ready
# After the 15-second alert duration and a scrape/evaluation interval:
curl -fsS http://127.0.0.1:19090/api/v1/alerts
# Fix the selector; preserve all other fields.
kubectl --context devops-oct7 -n capstone-oct7 patch service backend --type=merge \
  -p '{"spec":{"selector":{"app.kubernetes.io/component":"backend"}}}'
curl -fsS http://127.0.0.1:18080/ready
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
