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
