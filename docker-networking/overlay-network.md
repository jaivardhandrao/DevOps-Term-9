# Docker overlay networks

A bridge network joins containers on one Docker host. An overlay network joins containers that may
be running on different hosts. Docker creates a virtual layer over the physical networks and
encapsulates traffic between nodes, commonly with VXLAN.

## Where overlay networks are used

- Docker Swarm services spread across several nodes.
- Internal service-to-service traffic that should not depend on host IP addresses.
- Segmentation between application tiers across a cluster.

## How it works

1. The Docker hosts join the same Swarm and exchange cluster state.
2. An attachable or service overlay network is created with `docker network create --driver overlay`.
3. Each participating host creates the required virtual interfaces and forwarding rules.
4. A container sends traffic to another container's overlay address.
5. Docker encapsulates the frame, sends it between hosts, and decapsulates it at the destination.

Swarm provides service discovery through its internal DNS. Published services can also use the
routing mesh, allowing a request arriving at one node to reach a task on another node.

## Small Swarm example

```bash
docker swarm init --advertise-addr <manager-ip>
docker network create --driver overlay --attachable app-overlay
docker service create --name web --network app-overlay --replicas 3 nginx:alpine
docker service ps web
```

For a multi-host setup the nodes must be able to communicate on TCP 2377, TCP/UDP 7946, and UDP
4789. Overlay encryption can be requested with `--opt encrypted`, with some throughput cost.

I did not simulate a multi-host Swarm on one laptop because that would not demonstrate the main
point of the exercise: traffic crossing real Docker hosts.
