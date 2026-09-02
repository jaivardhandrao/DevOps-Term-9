# DevOps Homework

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117

This repository contains my work for the Linux, shell scripting, networking, Git, and Docker
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

## Verification

The scripts were linted before submission. Every Docker image was built and run locally, and
the Compose files were checked with `docker compose config`. The exact checks and observed output
are recorded inside the relevant folders.

No credentials are required by these exercises. The database used in the local networking lab
gets its disposable password from an untracked `.env` file.
