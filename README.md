# DevOps Homework

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117

This repository contains my work for the Linux, shell scripting, networking, Git, Docker, and Kubernetes
homework sessions. Each folder has the commands I used, short notes on what I observed, and the
files needed to repeat the exercise.

## Contents

| Topic | Work |
| --- | --- |
| Linux fundamentals | [Links, users, `journalctl`, and command notes](linux-fundamentals/README.md) |
| Shell scripting | [System information script](shell-scripting/README.md) |
| Networking | [Command practice and explanations](networking/README.md) |
| Git and GitHub | [`commit -a` and cherry-pick exercise](git-github/README.md) |
| Docker fundamentals | [Six Hello World applications](docker-apps/README.md) |
| Multi-stage build | [React build served by Nginx](multi-stage-build/README.md) |
| Networks and volumes | [Container networks, host mode, bind mount, and overlay notes](docker-networking/README.md) |
| Kubernetes fundamentals (session 9) | [Architecture and local lab setup](kubernetes-fundamentals/README.md) |
| Kubernetes core objects (session 10) | [Pods, ReplicaSets, Deployments, lifecycle, and release strategies](kubernetes-core-objects/README.md) |
| Kubernetes networking (session 11) | [Services, DNS, and troubleshooting](kubernetes-services/README.md) |
| Kubernetes configuration (session 12) | [Ingress, ConfigMaps, and Secrets](kubernetes-ingress-configmaps-secrets/README.md) |

The [Google Form answer sheet](SUBMISSION.md) maps every required field to its GitHub README link.

## Verification

The scripts were linted before submission. Every Docker image was built and run locally, and
the Compose files were checked with `docker compose config`. The exact checks and observed output
are recorded inside the relevant folders.

The Kubernetes work has separate [validation evidence](KUBERNETES-VALIDATION.md). The manifests and
lab instructions are prepared; live Kubernetes execution evidence is still pending. Examples of
expected behavior in those READMEs are not captured cluster output.

[Recorded local command-output images and raw logs](evidence/local-validation/README.md) show the
schema, API, and Docker checks. The same page links the student-run script for capturing actual
Kubernetes Terminal screenshots on a local cluster.

No external application credentials are required by these exercises. The database used in the
local networking lab gets its disposable password from an untracked `.env` file. The Kubernetes
Secret exercise creates its own disposable demonstration value in an ignored local file.
