# Offline Helm practice — October 7, 2026

These are excerpts from actual agent-operated local command output. No Kubernetes API connection or cluster mutation occurred. They do not establish installation or rollback success.

## Create a chart

The first attempt used a scratch parent directory that did not yet exist:

```text
$ ../.runtime/bin/helm create ../.runtime/helm/create-practice-20261007
Creating ../.runtime/helm/create-practice-20261007
Error: stat /Users/jaivardhandrao/Documents/Codex/2026-10-07/task/.runtime/helm: no such file or directory
```

After creating only that workspace scratch parent, the same operation succeeded:

```text
$ mkdir -p ../.runtime/helm && ../.runtime/bin/helm create ../.runtime/helm/create-practice-20261007
Creating ../.runtime/helm/create-practice-20261007
exit=0
```

The reusable driver now creates `scratch.parent` before calling `helm create`. The generated practice scaffold stays outside this repository; the submitted Notes chart is hand-authored.

## Configurable Service port and escaped page text

```text
$ ../.runtime/bin/helm template notes-a helm/notes-chart --set service.port=8088 --set-string app.message='A < B & C'
exit=0
```

Observed rendered fields:

```yaml
# ConfigMap HTML excerpt
<main><small>development</small><h1>Notes</h1><p>A &lt; B &amp; C</p></main></html>
# Service excerpt
name: notes-a-notes
ports:
  - {port: 8088, targetPort: http}
# Deployment excerpt
ports:
  - {name: http, containerPort: 80}
checksum/config: 3ae6d9d50367a27aa720f4aed1d4190dfec97bae2700b304b1ec0d06940c930f
```

The external Service port can change without breaking the named target's connection to Nginx port 80. `<` and `&` are escaped in the generated HTML.

## Content changes trigger a new Pod template

```text
$ ../.runtime/bin/helm template notes-a helm/notes-chart --set-string app.message='A changed note' --show-only templates/deployment.yaml
exit=0
```

For the same release name, the annotation changed to:

```yaml
checksum/config: ab8b3ecff94b861a502a52e2940701a38fecf0f9cb6f05622a4210fa64704718
```

This verifies a changed Pod template in the rendered manifest. A real cluster rollout has not been observed.

## Release isolation and production values

```text
$ ../.runtime/bin/helm template notes-b helm/notes-chart -f helm/notes-chart/values-prod.yaml
exit=0
```

Observed: three replicas, `ENVIRONMENT: "production"`, production HTML, resource names `notes-b-notes` / `notes-b-config`, and matching `app.kubernetes.io/instance: notes-b` selectors and Pod labels. They differ from the `notes-a` names/labels, so the rendered releases do not share resource names or selectors.
