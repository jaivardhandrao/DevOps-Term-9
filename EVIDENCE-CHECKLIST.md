# Coursework evidence and completion checklist

**Status recorded: 7 October 2026. Coverage is reported from actual evidence, not implementation alone.**

The current homework and Section A form have **20 topics covering sessions 1–21**. Sessions 1–2 share one field. [All 20 submitted main URLs](SUBMISSION.md) remain unchanged. The original September evidence is retained alongside new, explicitly agent-executed practicals.

## Requirement-by-requirement status

| Sessions | Supplied work and actual evidence | Remaining evidence or work |
| --- | --- | --- |
| 1–2 | Real hard/soft-link exercises, disposable Ubuntu user lifecycle, command practice and application-tagged journal entries | Specific-service journal remains unverified: the isolated node runs systemd/kubelet, but its bounded journal read was denied; no elevation attempted |
| 3 | The actual shell script accepted input and generated nonempty disk/process reports in a new Linux container | No additional execution gap identified |
| 4 | The networking script ran in a new container with actual DNS/HTTP/ICMP output | Container networking context is stated; no host-network equivalence claimed |
| 5 | Four main/two feature commits in an isolated repository; `commit -a` versus plain commit and selective cherry-pick verified | Actual Markdown commands/output satisfy the allowed evidence format |
| 6 | All six application images built and returned HTTP; genuine browser captures show each application | Browser captures prove visible applications, not Docker CLI state |
| 7 | Multi-stage image ran on loopback port 8080; `docker ps`, HTTP heading and absence of Node build tools verified; genuine browser capture | Three application types are demonstrated by the linked session 6 runs |
| 8 | All three networks, backend on two networks, frontend/backend/MySQL connectivity and database isolation verified; genuine bind-mount before/after images with same container and zero restarts | Apache directly on Mac host port 80 was unavailable and is not claimed; no host settings changed |
| 9 | Ready node, CoreDNS, default ServiceAccount/client and system Pods; retained authentic screenshot plus fresh command output | Retained screenshot is limited to what it shows; fresh native capture is unavailable |
| 10 | ReplicaSet replacement, all four deployment strategies and all 12 lifecycle/probe/init/sidecar/termination fixtures observed | Per-lifecycle-YAML screenshots required by the homework remain incomplete |
| 11 | All five Service types, internal HTTP/DNS and broken-selector recovery; comparison/FQDN/CoreDNS docs | Homework permits output or screenshots; command output is supplied. External LoadBalancer address/tunnel remains unverified |
| 12 | HTTP Ingress frontend/API, ConfigMap restart, Secret presence without disclosure, broken route and recovery; invalid label fixed | Actual healthy frontend browser screenshot supplied; API browser view was blocked, so fault/recovery screenshots remain incomplete. TLS is optional |
| 13 | PVC survived Pod replacement; probes and mini-project HTTP verified; HPA automatically scaled 2 → 5 → 2 under and after bounded CPU load | Command-output evidence is present; HPA screenshots remain incomplete |
| 14 | All nine issue categories observed with investigation/fix evidence; real HTTP-startup race found and corrected with a startup probe | Requested problem/fix screenshots remain incomplete |
| 15 | Helm create/repository practice, lint/render, install, two upgrades, failure/rollback, history, uninstall and healthy review reinstall; actual Notes browser capture | Browser image shows the app; CLI lifecycle is evidenced by actual transcripts |
| 16 | Full GitHub run at a218511 passed tests/builds, all scan gates, Helm+migrations, real CRUD, HPA metrics and cleanup | Genuine successful-run and completed-job browser screenshots supplied |
| 17 | Actual SAST/SCA/secrets/image gates pass; 44/42 prior HIGH matches remediated without exclusions; all negative controls pass | Full pipeline and genuine browser screenshots supplied. Required registry publication remains outside this pass |
| 18 | S3 Terraform layout, five AWS research READMEs, real provider validation/formatting and two mocked tests | Live AWS lifecycle and cloud screenshots require separate paid-cloud authorization |
| 19 | VPC/subnet/routes/security-group/EC2/S3 code and architecture, real provider validation/formatting and four mocked tests | Live AWS application/lifecycle/cleanup evidence remains pending |
| 20 | Healthy app metrics/dashboard; actual readiness alert fired and recovered; Argo Synced/Healthy at a218511 and automatically corrected deliberate configuration drift | Genuine corrected dashboard screenshot supplied; no notification to external recipients was sent |
| 21 | App tests/builds, genuine desktop/mobile UI, local Kubernetes Helm deployment, CRUD and PVC-preserving database replacement; HPA has valid metrics | Patched images, healthy UI/Grafana, GitOps self-heal, image/selector fault recovery and full CI verified; registry/cloud work and some command-state screenshots remain pending |

## Evidence and limitations

- Each session README links its actual output. Failed attempts remain alongside successful retries; timeouts are not silently converted into successful runs.
- [Security reports](final-devops-project/security/evidence/README.md) preserve before/after CVE findings and exact local image IDs. Local ARM64 results and independent GitHub AMD64 image scans are distinguished.
- [Full GitHub run 37664321492](https://github.com/jaivardhandrao/DevOps-Term-9/actions/runs/37664321492) uses `publish_images=false`. Tests, source/image gates and disposable Helm deployment/CRUD/HPA checks passed; the temporary CI cluster was destroyed.
- [Terraform S3](terraform-s3-demo/evidence/local-validation.txt), [EC2/VPC/S3](cloud-terraform/evidence/local-validation.txt) and [EKS](final-devops-project/terraform/evidence/local-validation.txt) results are **10 mocked tests**, not cloud deployment.
- The inline-image baseline was **5 of 20 submitted READMEs**. Coverage now reaches **12 of 20**: sessions 6–12, 15–17 and 20–21. Sessions allowing plain command output also have linked real transcripts. This image count is not an assignment-completion percentage; the remaining items above still matter.

## Execution boundaries

The original checkout under `Desktop/SST_CU/Term 9/devops/devops-homework` is untouched. Runtime work uses only the isolated `devops-oct7` Minikube profile, the `devops-oct7-capstone` Compose project and specifically named temporary evidence containers/repositories. The user's current Kubernetes context and unrelated projects, browser tabs and services are not changed.

The later coverage authorization resolved the earlier local practical/security approval blocks. Computer-use itself explicitly refuses `com.apple.Terminal`: “Computer Use is not allowed to use the app 'com.apple.Terminal' for safety reasons.” That restriction was not bypassed. Genuine application/GitHub browser captures use new owned tabs; actual command transcripts are not presented as native Terminal screenshots.

No AWS provisioning, registry publication, external deployment, form resubmission or messages to other people are performed by this coverage pass. Remaining cloud work needs a separate cost/access decision; EKS also needs reviewed operator/private-API/storage prerequisites and verified cleanup.
