# Kubernetes volumes

A container's writable layer is disposable. Kubernetes volumes give containers storage with a lifecycle chosen for the task. These manifests are teaching examples for the dedicated `devops-oct7` Minikube cluster.

| Mechanism | Lifetime / responsibility | Example here |
|---|---|---|
| `emptyDir` | Created with a Pod; survives a container restart but is removed with the Pod | `/scratch` in [examples.yaml](examples.yaml), `/tmp` in the web Deployment |
| `hostPath` | Mounts a path from one node; data stays on that node independently of the Pod | `/tmp/devops-advanced-volume-example` on the disposable Minikube node, mounted at `/node` |
| PersistentVolume (PV) | Cluster-level storage object representing a provisioned volume | Created by Minikube's dynamic provisioner for `advanced-data` |
| PersistentVolumeClaim (PVC) | Namespace-level request for storage capacity, access modes and a class | [`advanced-data`, 500 MiB RWO](../mini-project/pvc.yaml) |
| StorageClass | Describes a provisioner and storage policies | Minikube's `standard` class; inspect its provisioner and reclaim policy |
| Dynamic provisioning | Creates a matching PV automatically when an eligible PVC needs storage | Applying `advanced-data` produces a Bound PVC and backing PV without hand-writing a PV |

`hostPath` is node-specific and can expose sensitive host data if used carelessly. This example mounts only a purpose-named `/tmp` directory inside the disposable node; it does not mount the Mac filesystem. It is useful for understanding node storage, not a portable application persistence pattern.

## Commands and expected interpretation

These are instructions; actual output is in [the lab record](../evidence/storage-run.txt).

```bash
kubectl --context devops-oct7 -n devops-advanced apply -f kubernetes-storage-hpa-probes/01-kubernetes-volumes/examples.yaml
kubectl --context devops-oct7 -n devops-advanced exec volume-examples -- cat /scratch/example /node/example
kubectl --context devops-oct7 get storageclass
kubectl --context devops-oct7 -n devops-advanced get pvc
kubectl --context devops-oct7 get pv
```

The PVC should bind before the app becomes ready. A `Pending` PVC needs `describe pvc` and StorageClass inspection; an absent provisioner, mismatched access mode or delayed binding can explain the wait. The runner writes `Session 13 persistent marker` to `/data/student.txt`, records the original Pod UID, deletes that Pod and reads the same file from the current Pods. This tests Pod replacement, not backing disk failure, node replacement or disaster recovery.

Reclaim policy matters: a dynamically provisioned PV with `Delete` can delete backing data after its PVC is deleted. The runner leaves the PVC in place. Backups and deliberate retention are separate from replication and are not provided by this exercise.

References: [volumes](https://kubernetes.io/docs/concepts/storage/volumes/), [persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), [dynamic provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/).
