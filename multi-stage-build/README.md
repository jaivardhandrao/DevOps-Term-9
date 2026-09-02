# Multi-stage Docker build

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117

The first stage uses Node.js and Vite to create the static production files. The runtime stage
copies only `dist/` into Nginx, so Node.js, npm, and the source tree are not included in the final
image.

## Commands used

```bash
docker build -t devops-multi-stage ./multi-stage-build
docker run --rm -d --name devops-multi-stage -p 8080:80 devops-multi-stage
curl http://localhost:8080
docker ps --filter name=devops-multi-stage \
  --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker stop devops-multi-stage
```

The page displays `Hello World from Docker multi-stage build` at
`http://localhost:8080`. Output from the verified run is saved in [verification.txt](verification.txt).
