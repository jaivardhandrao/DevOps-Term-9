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
