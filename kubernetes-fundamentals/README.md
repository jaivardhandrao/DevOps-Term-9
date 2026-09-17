# Session 9: Kubernetes Fundamentals

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117
- **Status:** Live local evidence captured: node Ready, namespace/default ServiceAccount present, and client Pod Ready.

Kubernetes reconciles the desired state declared in API objects with the containers actually
running on worker nodes. For example, a Deployment requesting three replicas gives controllers
enough information to replace a lost Pod without manually starting a new container.

## Components

| Component | Responsibility |
| --- | --- |
| API server | Accepts authenticated requests and validates API objects. |
| etcd | Persists cluster configuration and state. |
| Scheduler | Chooses a suitable node for an unscheduled Pod. |
| Controller manager | Runs reconciliation loops, including Deployment and ReplicaSet controllers. |
| kubelet | Ensures the node's assigned containers run through the container runtime. |
| Container runtime | Pulls images and starts/stops containers, for example with containerd. |
| Cluster networking | A CNI implementation supplies Pod networking; kube-proxy or an alternative implements Service routing. |
| CoreDNS | Resolves cluster Service names. |

```text
kubectl -> API server -> stored desired state
                         |              |
                    controllers     scheduler
                         |              |
                         +---- Pod -----+
                                |
                         kubelet/runtime
```

An image packages an application. A container runs an image. A Pod is Kubernetes' scheduling
unit and can contain cooperating containers sharing networking and declared volumes. A node
hosts Pods; a cluster combines control-plane and worker components. A namespace groups API
objects but does not, by itself, isolate network traffic.

## Local lab setup

These commands are for the student to run on a disposable local Minikube lab with Docker,
Minikube, and kubectl installed. All subsequent exercise commands explicitly select the
`devops-coursework` context and `devops-homework` namespace. Do not substitute a shared or
cloud context. Cluster creation and `kubectl apply` persist cluster state.

From the repository root:

```bash
minikube start -p devops-coursework --driver=docker
kubectl --context=devops-coursework cluster-info
kubectl --context=devops-coursework get nodes -o wide
kubectl --context=devops-coursework get namespaces
kubectl --context=devops-coursework get pods -n kube-system
kubectl --context=devops-coursework apply -f kubernetes-fundamentals/namespace.yaml
```

Capture the real command output when running the lab. Check that the node is `Ready`, system
Pods are healthy, and the namespace exists. Node addresses and Pod names will differ by run.

## Reading YAML

`apiVersion` and `kind` identify the API resource. `metadata` supplies its name, namespace, and
labels. `spec` describes the desired configuration, while `status` is reported by the cluster.
Selectors match labels; a mismatch can leave a Service without ready destinations.

Continue with [session 10](../kubernetes-core-objects/README.md),
[session 11](../kubernetes-services/README.md), and
[session 12](../kubernetes-ingress-configmaps-secrets/README.md).

## Evidence and cleanup

![Actual Terminal screenshot: local Kubernetes node and client Pod ready](../evidence/live-checkpoints/01-fundamentals.png)

[Original transcript and screenshot context](../evidence/live-checkpoints/README.md) document
the student's successful fundamentals checks on `devops-evidence-20260917-210128`. The
screenshot also shows a macOS capture conflict that stopped the runner before session 10.

[Recorded local validation images and the student-run screenshot script](../evidence/local-validation/README.md)
are also available.

See [validation evidence](../KUBERNETES-VALIDATION.md) for checks actually performed. The setup
above uses a separate example profile; the actual evidence identifies the profile that ran.
After finishing and saving the required output, remove only the disposable lab you created.
For the example profile above:

```bash
minikube delete -p devops-coursework
```

References: [instructor session 9](https://github.com/Nency-Ravaliya/devops-heros/tree/1a24fe08c4956db0f8f22ffd6655581f7185699e/session9-k8s),
[Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/),
[Minikube setup](https://minikube.sigs.k8s.io/docs/start/).
