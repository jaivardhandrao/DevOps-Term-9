"""Run local checks and render their verbatim output; these are not desktop screenshots."""

import argparse
import json
import shlex
import subprocess
import sys
import tempfile
import textwrap
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/local-validation"
OUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--kubeconform", default="kubeconform")
args = parser.parse_args()
stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
lines = []


def run(command):
    lines.append("$ " + shlex.join(command))
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    lines.append(result.stdout.rstrip())
    lines.append(f"[exit {result.returncode}]")
    if result.returncode:
        raise RuntimeError(result.stdout)
    return result.stdout


def save(name, title):
    transcript = (
        f"{title}\nJaivardhan D. Rao | 24BCS10117\nRecorded: {stamp}\n\n"
        + "\n\n".join(lines)
        + "\n"
    )
    (OUT / f"{name}.txt").write_text(transcript)
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 19)
    wrapped = [
        part
        for line in transcript.splitlines()
        for part in (
            textwrap.wrap(
                line, width=118, replace_whitespace=False, drop_whitespace=False
            )
            or [""]
        )
    ]
    picture = Image.new("RGB", (1500, 110 + len(wrapped) * 28), "#121820")
    draw = ImageDraw.Draw(picture)
    for i, line in enumerate(wrapped):
        draw.text(
            (32, 26 + i * 28),
            line,
            font=font,
            fill="#82d5b3" if line.startswith("$") else "#e5edf6",
        )
    draw.text(
        (32, picture.height - 50),
        "Actual command output rendered as an image | No live Kubernetes cluster",
        font=font,
        fill="#a7b5c8",
    )
    picture.save(OUT / f"{name}.png")
    print(f"Saved {name}.png and verbatim transcript", flush=True)
    lines.clear()


run(
    [
        args.kubeconform,
        "-strict",
        "-summary",
        "-kubernetes-version",
        "1.34.0",
        "kubernetes-fundamentals",
        "kubernetes-core-objects",
        "kubernetes-services",
        "kubernetes-ingress-configmaps-secrets",
    ]
)
save("01-schema-validation", "Kubernetes manifest schema validation")
run([sys.executable, "scripts/validate-kubernetes.py"])
save("02-api-and-references", "API behavior and manifest relationship checks")

for component in ("frontend", "backend"):
    manifest = next(
        yaml.safe_load_all(
            (
                ROOT / f"kubernetes-ingress-configmaps-secrets/{component}.yaml"
            ).read_text()
        )
    )
    container = manifest["spec"]["template"]["spec"]["containers"][0]
    name = "devops-evidence-" + component + "-" + uuid.uuid4().hex[:8]
    with tempfile.TemporaryDirectory(prefix="devops-evidence-") as scratch:
        command = ["docker", "run", "--rm", "-d", "--network", "none", "--name", name]
        if component == "frontend":
            for item in container["env"]:
                command += ["-e", item["name"] + "=" + item["value"]]
            request = ["wget", "-qO-", "http://127.0.0.1/"]
        else:
            source = yaml.safe_load(
                (
                    ROOT / "kubernetes-ingress-configmaps-secrets/backend-code.yaml"
                ).read_text()
            )["data"]["app.py"]
            code = Path(scratch) / "app.py"
            code.write_text(source)
            command += ["-v", f"{code}:/app/app.py:ro"]
            for key, value in {
                "ENVIRONMENT": "coursework",
                "LOG_LEVEL": "INFO",
                "DEFAULT_CURRENCY": "INR",
                "DEMO_TOKEN": "public-test-fixture-not-a-credential",
            }.items():
                command += ["-e", key + "=" + value]
            request = [
                "python3",
                "-c",
                "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/api/health').read().decode())",
            ]
        command += [container["image"], *container["command"]]
        created = False
        try:
            run(command)
            created = True
            deadline = time.monotonic() + 30
            while True:
                probe = subprocess.run(
                    ["docker", "exec", name, *request],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
                if probe.returncode == 0:
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError("Container did not serve HTTP within 30 seconds")
                time.sleep(0.5)
            run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=" + name,
                    "--format",
                    "table {{.Names}}\t{{.Image}}\t{{.Status}}",
                ]
            )
            response = run(["docker", "exec", name, *request])
            if component == "frontend":
                assert response.strip() == "Hello from DevOps session 12 frontend"
            else:
                assert json.loads(response)["secret_loaded"] is True
                assert "public-test-fixture-not-a-credential" not in response
            run(
                [
                    "docker",
                    "image",
                    "inspect",
                    container["image"],
                    "--format",
                    "{{index .RepoDigests 0}}",
                ]
            )
        finally:
            if created:
                run(["docker", "rm", "-f", name])
        save(
            "03-frontend" if component == "frontend" else "04-backend",
            f"Actual Docker run: {component}",
        )
