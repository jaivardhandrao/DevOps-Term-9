# Kubernetes FQDNs

A fully qualified domain name identifies a name through the DNS hierarchy. In this lab,
`web-clusterip.devops-homework.svc.cluster.local` identifies Service `web-clusterip` in
namespace `devops-homework`. `cluster.local` is this cluster's DNS suffix, not a universal
hard-coded requirement.

| Caller | Name to try |
| --- | --- |
| Same namespace | `web-clusterip` |
| Another namespace | `web-clusterip.devops-homework` |
| Explicit absolute DNS name | `web-clusterip.devops-homework.svc.cluster.local.` |
| StatefulSet Pod behind headless Service | `stateful-web-0.web-headless.devops-homework.svc.cluster.local` |

The Pod's `/etc/resolv.conf` search list expands short names. A normal Service's DNS record
points to its ClusterIP; a headless Service returns Pod addresses. DNS resolution does not
guarantee that the selected Pods are ready or that the target port is correct.

From the repository root, the [session 11 evidence runner](../../scripts/run-coursework-labs.py)
records `nslookup`, resolver configuration, and actual HTTP requests from `dns-client`.
Read [the evidence index](../../evidence/october-7/README.md) for observed results.

Source: [Kubernetes DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/).
