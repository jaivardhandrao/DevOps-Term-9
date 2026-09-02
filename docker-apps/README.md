# Docker Hello World applications

The six applications are deliberately small so that each Dockerfile is easy to inspect. They use
different runtimes but return a webpage with the same basic idea.

| Folder | Runtime | Host port |
| --- | --- | ---: |
| `nodejs-app` | Node.js HTTP server | 8101 |
| `python-app` | Python HTTP server | 8102 |
| `java-app` | Java HTTP server | 8103 |
| `Apache-app` | Apache httpd | 8104 |
| `React-app` | React production build on Nginx | 8105 |
| `nginx-app` | Nginx static page | 8106 |

## Build and run one application

Run these commands from the repository root, changing the folder, image name, and port as needed:

```bash
docker build -t devops-node ./docker-apps/nodejs-app
docker run --rm -d --name devops-node -p 8101:3000 devops-node
curl http://localhost:8101
docker stop devops-node
```

The full set of commands I ran and their HTTP responses are in [verification.txt](verification.txt).
All containers used `--rm`, so stopping them also removed them.
