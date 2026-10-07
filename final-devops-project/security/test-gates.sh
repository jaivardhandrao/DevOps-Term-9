#!/usr/bin/env bash
# Negative controls stay in a disposable directory, outside tracked source.
set -euo pipefail
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
mkdir -p "$temporary/sast" "$temporary/secret" "$temporary/sca"
python3 - "$temporary" <<'PY'
import json
import pathlib
import sys
root = pathlib.Path(sys.argv[1])
(root / 'sast' / 'insecure.py').write_text('import hashlib\nhashlib.md5(b"negative control")\n')
# Deliberately nonfunctional synthetic credential; never a real account/key.
(root / 'secret' / 'fixture.env').write_text('aws_access_key_id=' + 'AK' + 'IA' + 'B' * 16 + '\n')
(root / 'sca' / 'package-lock.json').write_text(json.dumps({
    'name': 'negative-control', 'version': '1.0.0', 'lockfileVersion': 3,
    'packages': {'': {'dependencies': {'lodash': '4.17.20'}},
                 'node_modules/lodash': {'version': '4.17.20'}}}))
PY
expect_blocked() {
  local label=$1
  shift
  local status=0
  "$@" > "$temporary/command.log" 2>&1 || status=$?
  if [[ "$status" != 1 ]]; then
    printf '%s negative control failed: expected finding exit 1, got %s\n' "$label" "$status" >&2
    # Reports contain only generated dummy data; Gitleaks is always redacted.
    cat "$temporary/command.log" >&2
    exit 1
  fi
  printf 'PASS: %s rejected its negative control with exit 1\n' "$label"
}
expect_blocked SAST bandit -q -r "$temporary/sast" --severity-level medium
expect_blocked 'Secret scan' gitleaks dir "$temporary/secret" --redact=100 --no-banner
expect_blocked SCA trivy fs --scanners vuln --severity HIGH,CRITICAL --exit-code 1 --format json --output "$temporary/sca.json" "$temporary/sca"
# Trivy uses the same severity/exit gate for filesystem and image reports.
# Re-evaluate the real vulnerable dependency report to verify that report conversion
# cannot turn a HIGH finding into a successful gate. This is not an image scan.
expect_blocked 'Trivy report gate' trivy convert --severity HIGH,CRITICAL --exit-code 1 --format table "$temporary/sca.json"
