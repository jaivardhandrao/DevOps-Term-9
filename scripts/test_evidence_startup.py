"""Test startup with fake CLIs only; no cluster or screenshot tool is contacted."""

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
elif name == 'screencapture':
    sys.exit(73)  # Stop at the first screenshot checkpoint, without creating fake evidence.
"""


class StartupTest(unittest.TestCase):
    def execute(self, arguments=(), overrides=None):
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
        self.assertEqual(result.returncode, 73, result.stdout + result.stderr)
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
        self.assertEqual(result.returncode, 73, result.stdout + result.stderr)
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


if __name__ == "__main__":
    unittest.main()
