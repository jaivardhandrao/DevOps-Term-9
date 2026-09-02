# Networking command practice

I ran these checks from a disposable Linux container. That kept the output focused on the lab and
avoided publishing details about my laptop or home network. The captured output is in
[command-output.txt](command-output.txt).

| Command | What I checked |
| --- | --- |
| `hostname` | The current machine/container name. |
| `ip -brief address` | Interfaces, state, and assigned addresses. `lo` is loopback; `eth0` is the container interface. |
| `ip route` | How packets leave the host. The `default via` row identifies the gateway. |
| `nslookup example.com` | Whether DNS can translate a name to an IP address. |
| `ping -c 2 1.1.1.1` | Basic IP connectivity and round-trip time without relying on DNS. |
| `curl -I https://example.com` | DNS, TCP, TLS, and HTTP working together. `-I` fetches headers only. |
| `ss -tuln` | TCP/UDP sockets that are listening locally. |

The checks are collected in [`network-checks.sh`](network-checks.sh). On Linux it prefers `ip` and
`ss`; on macOS it falls back to `ifconfig` and `netstat`.

## What the output means

An interface address alone does not guarantee internet access. A usable route is also needed, DNS
must resolve names, and the destination service must accept the connection. Running `ping` by IP
before `nslookup` is a quick way to separate a routing problem from a DNS problem.

`ping` can still fail when the network is healthy because some hosts block ICMP. In that case I
check the real application path with `curl` and inspect the route with `traceroute` or `tracepath`.

## Useful troubleshooting order

```text
interface state -> local address -> default route -> DNS -> remote port -> application response
```

This order starts close to the machine and moves outward, which makes it easier to locate the
layer where the failure begins.
