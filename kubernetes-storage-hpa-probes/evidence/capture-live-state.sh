#!/bin/bash
# Read-only commands for genuine Terminal screenshots of the active lab.
set -eu
TASK_ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
export KUBECONFIG="$TASK_ROOT/.runtime/kube/config"
KUBECTL="$TASK_ROOT/.runtime/bin/kubectl"
HELM="$TASK_ROOT/.runtime/bin/helm"
date -u '+Observed live at %Y-%m-%d %H:%M:%S UTC'
case "${1:-storage}" in
  storage)
    set -x
    "$KUBECTL" --context devops-oct7 -n devops-advanced get hpa,pods,pvc
    "$KUBECTL" --context devops-oct7 -n devops-advanced top pods
    ;;
  troubleshooting)
    set -x
    "$KUBECTL" --context devops-oct7 -n devops-advanced get pods -o wide
    "$KUBECTL" --context devops-oct7 -n devops-advanced events --types=Warning
    ;;
  helm)
    set -x
    "$HELM" --kube-context devops-oct7 -n devops-helm history notes
    "$KUBECTL" --context devops-oct7 -n devops-helm get pods,services
    ;;
  *) echo 'Usage: capture-live-state.sh storage|troubleshooting|helm' >&2; exit 2 ;;
esac
