# Apache on the host network

Host mode removes the separate container network namespace. The container uses the host's network
stack directly, so there is no `ports:` mapping in the Compose file.

```bash
docker compose up -d
docker run --rm --network host alpine:3.20 wget -qO- http://127.0.0.1:80
docker compose down
```

This behaves most directly on Linux, where `curl http://localhost:80` can be used from the host.
Docker Desktop must have host-network forwarding enabled for that exact macOS/Windows host test.
The second host-network container still verifies the shared Docker host namespace without changing
that global setting. The result is in [verification.txt](verification.txt).

## Current verification boundary

The [7 October isolated runner](../evidence/live-20261007T181301Z.txt) found macOS port 80 unavailable and skipped starting a fresh host-network Apache listener. It did not stop an existing service or change Docker Desktop forwarding. The older transcript above proves the shared Docker Linux host namespace only; it is not evidence that macOS `localhost:80` worked. A direct macOS-host port-80 result and a corresponding screenshot remain outstanding.
