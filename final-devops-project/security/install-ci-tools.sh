#!/usr/bin/env bash
# Download versioned, checksum-verified binaries into a caller-owned directory.
set -euo pipefail
mode=${1:-security}
destination=${2:?usage: install-ci-tools.sh security|cluster DESTINATION}
mkdir -p "$destination"
destination=$(cd "$destination" && pwd)
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
fetch() { curl --fail --location --silent --show-error --retry 3 "$1" --output "$2"; }
verify() { (cd "$temporary" && sha256sum --check --status "$1"); }

if [[ "$mode" == security ]]; then
  trivy_archive=trivy_0.75.0_Linux-64bit.tar.gz
  fetch "https://github.com/aquasecurity/trivy/releases/download/v0.75.0/$trivy_archive" "$temporary/$trivy_archive"
  fetch https://github.com/aquasecurity/trivy/releases/download/v0.75.0/trivy_0.75.0_checksums.txt "$temporary/trivy-checksums.txt"
  awk -v name="$trivy_archive" '$2 == name {print}' "$temporary/trivy-checksums.txt" > "$temporary/selected.sha256"
  test -s "$temporary/selected.sha256"
  verify selected.sha256
  tar -xzf "$temporary/$trivy_archive" -C "$destination" trivy

  gitleaks_archive=gitleaks_8.30.1_linux_x64.tar.gz
  fetch "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/$gitleaks_archive" "$temporary/$gitleaks_archive"
  fetch https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_checksums.txt "$temporary/gitleaks-checksums.txt"
  awk -v name="$gitleaks_archive" '$2 == name {print}' "$temporary/gitleaks-checksums.txt" > "$temporary/selected.sha256"
  test -s "$temporary/selected.sha256"
  verify selected.sha256
  tar -xzf "$temporary/$gitleaks_archive" -C "$destination" gitleaks
elif [[ "$mode" == cluster ]]; then
  fetch https://github.com/kubernetes-sigs/kind/releases/download/v0.33.0/kind-linux-amd64 "$temporary/kind-linux-amd64"
  fetch https://github.com/kubernetes-sigs/kind/releases/download/v0.33.0/kind-linux-amd64.sha256sum "$temporary/selected.sha256"
  verify selected.sha256
  install -m 0755 "$temporary/kind-linux-amd64" "$destination/kind"

  fetch https://dl.k8s.io/release/v1.34.11/bin/linux/amd64/kubectl "$temporary/kubectl"
  fetch https://dl.k8s.io/release/v1.34.11/bin/linux/amd64/kubectl.sha256 "$temporary/kubectl.sha256"
  printf '%s  kubectl\n' "$(cat "$temporary/kubectl.sha256")" > "$temporary/selected.sha256"
  verify selected.sha256
  install -m 0755 "$temporary/kubectl" "$destination/kubectl"

  fetch https://get.helm.sh/helm-v4.3.0-linux-amd64.tar.gz "$temporary/helm-v4.3.0-linux-amd64.tar.gz"
  fetch https://get.helm.sh/helm-v4.3.0-linux-amd64.tar.gz.sha256sum "$temporary/selected.sha256"
  verify selected.sha256
  tar -xzf "$temporary/helm-v4.3.0-linux-amd64.tar.gz" -C "$temporary" linux-amd64/helm
  install -m 0755 "$temporary/linux-amd64/helm" "$destination/helm"
else
  printf 'Unsupported tool group: %s\n' "$mode" >&2
  exit 2
fi
