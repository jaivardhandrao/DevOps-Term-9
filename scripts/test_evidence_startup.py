"""Test startup/capture recovery with fake CLIs; no cluster or screen is contacted."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("run-local-kubernetes-evidence.sh")
PROFILE = "devops-evidence-20260917-210128"
MOCK = r"""
import json, os, sys
from pathlib import Path
name = Path(sys.argv[0]).name
args = sys.argv[1:]
folder = Path(os.environ['MOCK_STATE'])
with (folder / 'calls.jsonl').open('a') as log:
    log.write(json.dumps([name, *args]) + '\n')
if name == 'docker':
    print('unix:///tmp/test-only.sock')
elif name == 'kubectl':
    if 'config' in args:
        print(os.environ.get('MOCK_SERVER', 'https://127.0.0.1:59986'))
    elif 'nodes' in args and 'wait' in args:
        if os.environ.get('FAIL_NODE'): sys.exit(20)
        (folder / 'node-ready').touch()
    elif 'serviceaccount/default' in args and 'wait' in args:
        if os.environ.get('FAIL_SA'): sys.exit(21)
        (folder / 'serviceaccount-created').touch()
    elif 'kubernetes-services/client.yaml' in args:
        if not (folder / 'node-ready').exists() or not (folder / 'serviceaccount-created').exists():
            print('Forbidden: default serviceaccount not found')
            sys.exit(22)
    elif 'kubernetes-core-objects/pod.yaml' in args:
        sys.exit(74)  # Stop just after the first screenshot checkpoint.
elif name == 'screencapture':
    count_file = folder / 'capture-count'
    count = int(count_file.read_text()) + 1 if count_file.exists() else 1
    count_file.write_text(str(count))
    if os.environ.get('CAPTURE_MODE') == 'busy-then-success' and count > 1:
        Path(args[-1]).write_bytes(b'temporary test fixture, not a screenshot')
    elif os.environ.get('CAPTURE_MODE') != 'empty-success':
        print('screencapture: cannot run two interactive screen captures at a time')
        sys.exit(73)
"""


class StartupTest(unittest.TestCase):
    def execute(self, arguments=(), overrides=None, input_text=""):
        scratch = tempfile.TemporaryDirectory(prefix="devops-startup-test-")
        self.addCleanup(scratch.cleanup)
        root = Path(scratch.name)
        (root / "scripts").mkdir()
        shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
        binaries = root / "bin"
        binaries.mkdir()
        mock = binaries / "fake-cli"
        mock.write_text(f"#!{sys.executable}\n" + MOCK)
        mock.chmod(0o755)
        for name in ("docker", "kubectl", "minikube", "screencapture"):
            (binaries / name).symlink_to(mock)
        old_log = root / "evidence/live" / PROFILE / "run.txt"
        old_log.parent.mkdir(parents=True)
        old_log.write_text("original failed attempt\n")
        environment = {
            **os.environ,
            "PATH": f"{binaries}:{os.environ['PATH']}",
            "MOCK_STATE": str(root),
            "DOCKER_HOST": "",
        }
        environment.update(overrides or {})
        result = subprocess.run(
            ["bash", str(root / "scripts" / SCRIPT.name), *arguments],
            env=environment,
            capture_output=True,
            text=True,
            input=input_text,
            check=False,
            timeout=20,
        )
        calls_file = root / "calls.jsonl"
        calls = (
            [json.loads(line) for line in calls_file.read_text().splitlines()]
            if calls_file.exists()
            else []
        )
        self.assertEqual(old_log.read_text(), "original failed attempt\n")
        return result, calls

    def test_fresh_start_waits_before_creating_client(self):
        result, calls = self.execute()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(any(c[0] == "screencapture" for c in calls))
        self.assertTrue(any(c[0] == "minikube" and "start" in c for c in calls))
        node_wait = next(i for i, c in enumerate(calls) if "nodes" in c and "wait" in c)
        sa_wait = next(
            i
            for i, c in enumerate(calls)
            if "serviceaccount/default" in c and "wait" in c
        )
        client = next(
            i for i, c in enumerate(calls) if "kubernetes-services/client.yaml" in c
        )
        self.assertLess(node_wait, sa_wait)
        self.assertLess(sa_wait, client)

    def test_resume_does_not_start_another_cluster(self):
        result, calls = self.execute(("--resume", PROFILE))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(any(c[0] == "screencapture" for c in calls))
        self.assertFalse(any(c[0] == "minikube" and "start" in c for c in calls))
        self.assertTrue(any("kubernetes-services/client.yaml" in c for c in calls))

    def test_unready_node_stops_before_apply(self):
        result, calls = self.execute(overrides={"FAIL_NODE": "1"})
        self.assertEqual(result.returncode, 20)
        self.assertFalse(any("apply" in c for c in calls))

    def test_missing_serviceaccount_stops_before_client(self):
        result, calls = self.execute(overrides={"FAIL_SA": "1"})
        self.assertEqual(result.returncode, 21)
        self.assertFalse(any("kubernetes-services/client.yaml" in c for c in calls))

    def test_remote_resume_context_is_rejected(self):
        result, calls = self.execute(
            ("--resume", PROFILE), {"MOCK_SERVER": "https://remote.example.test:6443"}
        )
        self.assertEqual(result.returncode, 1)
        self.assertFalse(any("apply" in c for c in calls))

    def test_invalid_resume_arguments_do_not_call_tools(self):
        for arguments in (("--resume", "production"), ("--resume",)):
            with self.subTest(arguments=arguments):
                result, calls = self.execute(arguments)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(calls, [])

    def test_busy_picker_can_retry_without_restarting_cluster(self):
        result, calls = self.execute(
            overrides={"CAPTURE_MODE": "busy-then-success"}, input_text="\n"
        )
        self.assertEqual(result.returncode, 74, result.stdout + result.stderr)
        self.assertEqual(sum(c[0] == "screencapture" for c in calls), 2)
        self.assertEqual(sum(c[0] == "minikube" and "start" in c for c in calls), 1)

    def test_saved_png_can_replace_busy_picker(self):
        with tempfile.TemporaryDirectory(prefix="manual screenshot test ") as folder:
            # Deliberately a signature-only fixture, never published as evidence.
            manual = Path(folder) / "manual fixture.png"
            fixture = b"\x89PNG\r\n\x1a\nunit-test-only"
            manual.write_bytes(fixture)
            result, calls = self.execute(input_text=f"{manual}\n")
            self.assertEqual(result.returncode, 74, result.stdout + result.stderr)
            capture_call = next(c for c in calls if c[0] == "screencapture")
            self.assertEqual(Path(capture_call[-1]).read_bytes(), fixture)

    def test_missing_or_non_png_file_does_not_advance_lab(self):
        with tempfile.TemporaryDirectory() as folder:
            invalid = Path(folder) / "invalid.png"
            invalid.write_text("not an image")
            result, calls = self.execute(input_text=f"{folder}/missing.png\n{invalid}\n")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("Could not use screenshot", result.stdout)
            self.assertFalse(any("kubernetes-core-objects/pod.yaml" in c for c in calls))

    def test_cancelled_picker_with_zero_exit_still_requires_a_file(self):
        result, calls = self.execute(overrides={"CAPTURE_MODE": "empty-success"})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Screenshot still pending", result.stdout)
        self.assertFalse(any("kubernetes-core-objects/pod.yaml" in c for c in calls))


class ReadRetryTest(unittest.TestCase):
    def run_probe(self, succeeds_on):
        # Load only the read-retry function; never execute the lab or a real CLI.
        source = SCRIPT.read_text()
        retry = "retry_read() {" + source.split("retry_read() {", 1)[1].split(
            "\ncapture() {", 1
        )[0]
        shell = f"""set -euo pipefail
{retry}
sleep() {{ :; }}
count=0
probe() {{ count=$((count + 1)); printf 'probe=%s\\n' "$count"; [[ "$count" == {succeeds_on} ]]; }}
retry_read probe
printf 'next-checkpoint\\n'
"""
        return subprocess.run(
            ["bash", "-c", shell], capture_output=True, text=True, check=False, timeout=5
        )

    def test_transient_read_failure_recovers(self):
        result = self.run_probe(3)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("probe="), 3)
        self.assertIn("next-checkpoint", result.stdout)

    def test_persistent_read_failure_stops_at_limit(self):
        result = self.run_probe(99)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("probe="), 15)
        self.assertNotIn("next-checkpoint", result.stdout)


if __name__ == "__main__":
    unittest.main()
