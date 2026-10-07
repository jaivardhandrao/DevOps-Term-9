# Docker networking and volumes

This folder contains four separate exercises:

1. [Three containers on three networks](container-networking/README.md)
2. [Apache using the host network](host-network/README.md)
3. [An Nginx bind mount](bind-mount/README.md)
4. [Overlay network notes](overlay-network.md)

I kept each Compose project separate because host networking and bridge networking are easier to
inspect when their resources are not mixed together.

The database password for the first exercise is read from `.env`. Only `.env.example` is tracked;
the real local value is not committed.

## Fresh isolated run — 7 October 2026

[Raw commands and output](evidence/live-20261007T181301Z.txt) verify the three-network topology, both intended connections, direct database isolation by DNS and TCP address, and a bind-mount update with unchanged container ID and zero restarts. The [bind-mount README](bind-mount/README.md#fresh-browser-evidence--7-october-2026) embeds genuine before/after browser captures.

Actual bind-mounted Nginx page before the scratch file edit:

![Live bind-mounted page before editing the file](bind-mount/evidence/screenshots/2026-10-07-before.jpg)

Actual page after the file edit, with the same container ID and zero restarts:

![Live bind-mounted page after editing the file](bind-mount/evidence/screenshots/2026-10-07-after.jpg)

Reproduce from the repository root: `python3 scripts/run-foundation-evidence.py --topic docker-networking --browser-checkpoints --pause`. This creates new uniquely named containers/networks and a disposable MySQL data directory, using a generated database password without reading it. It does not consume an existing database or `.env`. The live test uses Nginx as the backend on port 80 while preserving the same network topology as the Compose exercise.

The fresh host-network Apache check was skipped because macOS port 80 was unavailable; existing services and Docker Desktop settings were left unchanged. Earlier shared-Docker-host evidence remains in [host-network/verification.txt](host-network/verification.txt); direct macOS host port 80 is not newly verified.

Earlier unsuccessful attempts remain available: [missing Alpine httpd applet](evidence/live-20261007T180106Z.txt), [bind-mount propagation timing](evidence/live-20261007T181128Z.txt). The final runner uses a known Nginx image and bounded expected-content polling before asserting the update.
