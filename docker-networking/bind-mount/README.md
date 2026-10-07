# Nginx bind mount

The local `site/` folder is mounted over Nginx's document root. A file edit appears immediately
because Nginx reads the same host file on the next request; the image is not rebuilt and the
container is not restarted.

```bash
docker compose up -d
curl http://localhost:8082

# Edit site/index.html, then request it again.
curl http://localhost:8082
docker compose down
```

The before/after responses and unchanged container ID are in [verification.txt](verification.txt).

## Fresh browser evidence — 7 October 2026

These unaltered screenshots show the actual page at `http://127.0.0.1:55018` before and after editing the mounted scratch file. The [raw transcript](../evidence/live-20261007T181301Z.txt) records the same container ID `e408267216f4…` and restart count `0` on both sides. The temporary container and scratch directory were removed after capture. On Docker Desktop, the runner waits for expected content to propagate before asserting the result.

Before the host file edit:

![Live bind-mounted page before the file edit](evidence/screenshots/2026-10-07-before.jpg)

After the host file edit, with no image rebuild or container restart:

![Live bind-mounted page after the file edit](evidence/screenshots/2026-10-07-after.jpg)
