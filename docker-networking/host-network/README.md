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
