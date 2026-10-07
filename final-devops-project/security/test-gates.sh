#!/usr/bin/env bash
# Negative controls stay in a disposable directory, outside tracked source.
set -euo pipefail
mode=${1:-all}
if [[ "$mode" != all && "$mode" != local ]]; then
  printf 'Usage: test-gates.sh [all|local]\n' >&2
  exit 2
fi
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
# Distinct characters exceed the detector's entropy floor; repeated filler would
# be correctly filtered as a placeholder and would not exercise the gate.
(root / 'secret' / 'fixture.env').write_text('aws_access_key_id=' + 'AK' + 'IA' + ''.join(chr(i) for i in range(66, 82)) + '\n')
(root / 'sca' / 'package-lock.json').write_text(json.dumps({
    'name': 'negative-control', 'version': '1.0.0', 'lockfileVersion': 3,
    'packages': {'': {'dependencies': {'lodash': '4.17.20'}},
                 'node_modules/lodash': {'version': '4.17.20'}}}))
PY
expect_blocked() {
  local label=$1
  local expected=$2
  shift 2
  local status=0
  "$@" > "$temporary/command.log" 2>&1 || status=$?
  if [[ "$status" != "$expected" ]]; then
    printf '%s negative control failed: expected finding exit %s, got %s\n' "$label" "$expected" "$status" >&2
    # Reports contain only generated dummy data; Gitleaks is always redacted.
    cat "$temporary/command.log" >&2
    exit 1
  fi
  printf 'PASS: %s rejected its negative control with exit %s\n' "$label" "$expected"
}
expect_blocked SAST 1 bandit -q -r "$temporary/sast" --severity-level medium --format json --output "$temporary/sast.json"
expect_blocked 'Secret scan' 42 gitleaks dir "$temporary/secret" --redact=100 --no-banner --exit-code 42 --report-format json --report-path "$temporary/secret.json"
python3 - "$temporary" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
assert any(item['test_id'] == 'B324' for item in json.loads((root/'sast.json').read_text())['results'])
assert any(item['RuleID'] == 'aws-access-token' for item in json.loads((root/'secret.json').read_text()))
print('PASS: SAST and secret JSON contain the intended weak-crypto and synthetic-key findings')
PY
if [[ "$mode" == local ]]; then
  printf 'LOCAL ONLY: dependency and Trivy report controls were not executed\n'
  exit 0
fi
expect_blocked SCA 42 trivy fs --scanners vuln --severity HIGH,CRITICAL --exit-code 42 --format json --output "$temporary/sca.json" "$temporary/sca"
python3 - "$temporary/sca.json" <<'PY'
import json, sys
report = json.load(open(sys.argv[1]))
assert any(v['PkgName'] == 'lodash' and v['InstalledVersion'] == '4.17.20' and v['Severity'] in {'HIGH', 'CRITICAL'}
           for result in report.get('Results', []) for v in result.get('Vulnerabilities', []))
print('PASS: SCA JSON contains the intended vulnerable lodash dependency')
PY
# Trivy uses the same severity/exit gate for filesystem and image reports.
# Re-evaluate the real vulnerable dependency report to verify that report conversion
# cannot turn a HIGH finding into a successful gate. This is not an image scan.
expect_blocked 'Trivy report gate' 42 trivy convert --severity HIGH,CRITICAL --exit-code 42 --format table "$temporary/sca.json"
