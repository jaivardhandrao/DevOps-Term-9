# CoreDNS

CoreDNS is the cluster DNS server. Its Kubernetes plugin watches API objects and answers
Service and Pod discovery queries. The Corefile controls plugins such as `kubernetes`,
`forward`, `cache`, `health`, and `ready`; external queries normally go to upstream resolvers.

Debug in this order: inspect the caller's resolver, query the full Service name, check the DNS
Service and CoreDNS Pods, inspect CoreDNS logs/Corefile, then test endpoints and network policy.
An empty application EndpointSlice and an unavailable DNS server are different failures.

```bash
kubectl --context=devops-oct7 -n devops-homework exec dns-client -- cat /etc/resolv.conf
kubectl --context=devops-oct7 -n devops-homework exec dns-client -- nslookup kubernetes.default.svc.cluster.local
kubectl --context=devops-oct7 -n kube-system get deployment,pods,service -l k8s-app=kube-dns
kubectl --context=devops-oct7 -n kube-system get configmap coredns -o yaml
kubectl --context=devops-oct7 -n kube-system logs deployment/coredns --tail=30
```

The [recording script](../../scripts/run-coursework-labs.py) checks the CoreDNS rollout and
captures working Service queries. See [observed evidence](../../evidence/october-7/README.md).

Source: [Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/).
