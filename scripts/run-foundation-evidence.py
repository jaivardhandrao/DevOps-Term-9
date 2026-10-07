#!/usr/bin/env python3
"""Run current commands in new, disposable coursework labs, never replay stored output."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
from pathlib import Path
import re
import shlex
import shutil
import socket
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {"linux": "linux-fundamentals", "shell": "shell-scripting", "networking": "networking",
          "git": "git-github", "docker": "docker-apps", "multistage": "multi-stage-build",
          "docker-networking": "docker-networking"}
LAB_IMAGE = "devops-term9-foundation-lab:20261007"

class Lab:
    def __init__(self, topic):
        self.prefix = "term9-evidence-" + uuid.uuid4().hex[:10]
        self.scratch = Path(tempfile.mkdtemp(prefix=self.prefix + "-"))
        self.containers, self.networks, self.images, self.observations = [], [], [], []
        directory = ROOT / TOPICS[topic] / "evidence"
        directory.mkdir(exist_ok=True)
        self.path = directory / ("live-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".txt")
        self.log = self.path.open("w")

    def say(self, text):
        print(text, flush=True)
        self.log.write(text + "\n")
        self.log.flush()

    def run(self, args, *, cwd=None, input=None, check=True, timeout=900, quiet=False):
        self.say("\n$ " + shlex.join(str(x) for x in args))
        result = subprocess.run(args, cwd=cwd or ROOT, input=input, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        output = result.stdout.rstrip()
        if output:
            self.log.write(output + "\n")
            self.log.flush()
            print(output[-2500:] if quiet else output, flush=True)
            if quiet and len(output) > 2500:
                print("[Earlier build output is retained in the raw transcript.]", flush=True)
        self.say(f"[exit {result.returncode}]")
        if check and result.returncode:
            raise RuntimeError(f"Command exited {result.returncode}: {shlex.join(args)}")
        return result

    def container(self, suffix, image, args=None, *, options=None, detached=False, input=None):
        name = self.prefix + "-" + suffix
        self.containers.append(name)
        command = ["docker", "run", "--name", name, "--label", "devops.coursework.run=" + self.prefix]
        command += ["-d"] if detached else ["--rm", "-i"]
        command += options or []
        command += [image] + (args or [])
        return name, self.run(command, input=input)

    def image(self, path, suffix):
        image = self.prefix + "-" + suffix + ":local"
        self.images.append(image)
        self.run(["docker", "build", "--quiet", "-t", image, str(path)], quiet=True)
        return image

    def wait(self, args, tries=30, expected=None):
        for _ in range(tries):
            result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode == 0 and (expected is None or expected in result.stdout):
                verified = self.run(args)
                if expected is None or expected in verified.stdout:
                    return verified
            time.sleep(1)
        result = self.run(args)
        if expected is not None and expected not in result.stdout:
            raise RuntimeError(f"Expected response content did not become ready: {expected}")
        return result

    def cleanup(self):
        for kind, names in [(["rm", "-f"], self.containers), (["network", "rm"], self.networks), (["image", "rm"], self.images)]:
            for name in reversed(names):
                subprocess.run(["docker"] + kind + [name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(self.scratch)

def ensure_lab(lab):
    lab.run(["docker", "build", "--quiet", "-t", LAB_IMAGE, str(ROOT / "linux-fundamentals/evidence")], quiet=True)

def linux(lab):
    ensure_lab(lab)
    code = r"""set -euxo pipefail
printf '\n== Links ==\n'
mkdir links
printf 'link exercise\n' > links/original
ln links/original links/hard
ln -s original links/soft
ls -li links
test "$(stat -c %i links/original)" = "$(stat -c %i links/hard)"
rm links/original
cat links/hard
test -L links/soft && test ! -e links/soft
printf 'PASS: hard link survives deletion; symbolic link is dangling\n'
rm links/hard links/soft
rmdir links
printf '\n== Disposable-container user only ==\n'
adduser --disabled-password --gecos 'Coursework demonstration' courseworkdemo
id courseworkdemo
getent passwd courseworkdemo
deluser courseworkdemo
rm -r /home/courseworkdemo
if getent passwd courseworkdemo; then exit 1; fi
printf 'PASS: temporary container account removed; host accounts unchanged\n'
printf '\n== Files, search, archives, identity, disk and processes ==\n'
pwd
mkdir files
printf 'hello students\n' > files/notes.txt
cp files/notes.txt files/copied.txt
mv files/copied.txt files/moved.txt
ls -la files
grep -n students files/notes.txt
head -n 1 files/notes.txt
tar -czf notes.tar.gz files
tar -tzf notes.tar.gz
file notes.tar.gz
whoami
id
df -h /lab
free -h
ps -eo pid,ppid,user,comm
printf '\n== Container application journal ==\n'
mkdir -p /run/systemd/journal
/usr/lib/systemd/systemd-journald >/tmp/journald-start.txt 2>&1 &
journal_pid=$!
sleep 1
printf 'Started isolated coursework application\n' | systemd-cat -t coursework-demo
printf 'Application health check succeeded\n' | systemd-cat -t coursework-demo
sleep 1
journalctl --no-pager -t coursework-demo -n 5
journalctl --no-pager -u coursework-demo.service -n 5
journalctl --disk-usage
kill "$journal_pid"
printf 'LIMIT: systemd is not PID 1; these are real tagged application entries, not a systemd-managed service.\n'
"""
    lab.container("linux", LAB_IMAGE, ["bash", "-s"], options=["--network", "none"], input=code)
    lab.observations += ["Hard/soft links and disposable Ubuntu user lifecycle verified.",
                         "Real application-tagged journal captured. A systemd-managed service is not claimed."]

def shell(lab):
    ensure_lab(lab)
    code = "printf 'Jaivardhan D. Rao\\n24BCS10117\\n' | bash /coursework/system-info.sh; test -s system-report/processes.txt; test -s system-report/summary.txt; printf '\\nPASS: both generated reports are nonempty\\n'"
    lab.container("shell", LAB_IMAGE, ["bash", "-euo", "pipefail", "-c", code],
                  options=["--network", "none", "--mount", f"type=bind,src={ROOT / 'shell-scripting/system-info.sh'},dst=/coursework/system-info.sh,readonly"])
    lab.observations.append("The actual repository script accepted input and generated disk/process reports inside the new Linux container.")

def networking(lab):
    ensure_lab(lab)
    lab.container("network", LAB_IMAGE, ["bash", "/coursework/network-checks.sh"],
                  options=["--mount", f"type=bind,src={ROOT / 'networking/network-checks.sh'},dst=/coursework/network-checks.sh,readonly"])
    lab.observations.append("The repository networking script ran in a fresh container, including example.com DNS/HTTP and 1.1.1.1 ICMP.")

def git(lab):
    work = lab.scratch / "repository"
    lab.run(["git", "init", "-b", "main", str(work)])
    for key, value in [("user.name", "Coursework Demonstration"), ("user.email", "coursework@example.invalid"), ("commit.gpgsign", "false")]:
        lab.run(["git", "config", key, value], cwd=work)
    for name in ["base", "linux", "docker"]:
        with (work / "notes.txt").open("a") as stream:
            stream.write(name + "\n")
        lab.run(["git", "add", "notes.txt"], cwd=work)
        lab.run(["git", "commit", "-m", "Add " + name + " note"], cwd=work)
    (work / "untracked.txt").write_text("not staged by commit -a\n")
    with (work / "notes.txt").open("a") as stream:
        stream.write("tracked modification\n")
    result = lab.run(["git", "commit", "-m", "Unstaged change test"], cwd=work, check=False)
    assert result.returncode != 0
    lab.run(["git", "commit", "-a", "-m", "Include tracked change only"], cwd=work)
    assert "?? untracked.txt" in lab.run(["git", "status", "--short"], cwd=work).stdout
    lab.run(["git", "switch", "-c", "command-notes"], cwd=work)
    (work / "networking.txt").write_text("DNS resolves names to addresses\n")
    lab.run(["git", "add", "networking.txt"], cwd=work)
    lab.run(["git", "commit", "-m", "Add networking note"], cwd=work)
    chosen = lab.run(["git", "rev-parse", "HEAD"], cwd=work).stdout.strip()
    (work / "journaling.txt").write_text("journalctl reads systemd journals\n")
    lab.run(["git", "add", "journaling.txt"], cwd=work)
    lab.run(["git", "commit", "-m", "Add journaling note"], cwd=work)
    lab.run(["git", "log", "--oneline", "--all", "--graph", "--decorate"], cwd=work)
    lab.run(["git", "switch", "main"], cwd=work)
    lab.run(["git", "cherry-pick", "-x", chosen], cwd=work)
    lab.run(["git", "log", "--oneline", "-5"], cwd=work)
    lab.run(["git", "show", "HEAD:networking.txt"], cwd=work)
    assert (work / "networking.txt").exists() and not (work / "journaling.txt").exists()
    lab.observations.append("Four main commits and two feature commits created. Plain commit rejected unstaged changes; commit -a left the new file untracked; cherry-pick copied only the selected feature change.")

def free_port(port):
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False

def start_http(lab, image, suffix, container_port, host_port=0):
    name, _ = lab.container(suffix, image, detached=True, options=["-p", f"127.0.0.1:{host_port}:{container_port}"])
    binding = lab.run(["docker", "port", name, f"{container_port}/tcp"]).stdout.strip()
    url = "http://" + binding
    response = lab.wait(["curl", "--fail", "--silent", "--show-error", "--max-time", "3", url])
    return name, url, response.stdout

def docker(lab):
    for folder, port, heading in [("nodejs-app", 3000, "Node.js"), ("python-app", 8000, "Python"), ("java-app", 8080, "Java"),
                                 ("Apache-app", 80, "Apache"), ("React-app", 80, "React"), ("nginx-app", 80, "Nginx")]:
        image = lab.image(ROOT / "docker-apps" / folder, folder.lower())
        name, url, body = start_http(lab, image, folder.lower(), port)
        if folder == "React-app":
            match = re.search(r'src="([^"]+\.js)"', body)
            assert match, "React production script missing from HTML"
            bundle_path = lab.scratch / "react-production.js"
            lab.run(["curl", "-fsS", "-o", str(bundle_path), url + match.group(1)])
            bundle = bundle_path.read_text()
            assert "Hello World from React" in bundle
            lab.say(f"PASS: fetched {bundle_path.stat().st_size}-byte production bundle; SHA256={hashlib.sha256(bundle.encode()).hexdigest()}; Hello World from React present.")
        else:
            assert "Hello World from " + heading in body
        lab.run(["docker", "ps", "--filter", "name=^/" + name + "$", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
        lab.observations.append(f"{heading}: fresh image build and HTTP response at {url}.")

def multistage(lab):
    if not free_port(8080):
        raise RuntimeError("Port 8080 is unavailable; no existing service changed. Historical port-8080 evidence remains in verification.txt.")
    image = lab.image(ROOT / "multi-stage-build", "multistage")
    name, url, body = start_http(lab, image, "multistage", 80, 8080)
    assert "Hello World from Docker multi-stage build" in body
    lab.run(["docker", "ps", "--filter", "name=^/" + name + "$", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
    lab.run(["docker", "exec", name, "sh", "-c", "test ! -e /usr/local/bin/node && test ! -d /app/node_modules && echo 'PASS: Nginx runtime has no Node build toolchain'"])
    lab.observations.append("Exact required heading served on 127.0.0.1:8080; docker ps confirmed the mapping.")

def docker_networking(lab):
    for suffix in ["front", "app", "db"]:
        name = lab.prefix + "-" + suffix
        lab.run(["docker", "network", "create", "--label", "devops.coursework.run=" + lab.prefix, name])
        lab.networks.append(name)
    front_net, app_net, db_net = lab.networks
    front, _ = lab.container("frontend", "alpine:3.20", ["sleep", "3600"], detached=True, options=["--network", front_net])
    lab.run(["docker", "network", "connect", app_net, front])
    back, _ = lab.container("backend", "nginx:1.27-alpine",
                           ["sh", "-c", "printf 'Hello from the backend container\\n' >/usr/share/nginx/html/index.html; exec nginx -g 'daemon off;'"],
                           detached=True, options=["--network", app_net, "--network-alias", "backend"])
    lab.run(["docker", "network", "connect", db_net, back])
    database, _ = lab.container("database", "mysql:8.4", detached=True,
                  options=["--network", db_net, "--network-alias", "database", "--tmpfs", "/var/lib/mysql", "-e", "MYSQL_RANDOM_ROOT_PASSWORD=yes"])
    lab.wait(["docker", "exec", front, "wget", "-qO-", "http://backend:80"])
    lab.wait(["docker", "exec", back, "nc", "-zvw", "2", "database", "3306"], tries=100)
    lab.run(["docker", "exec", front, "sh", "-c", "if nslookup database >/dev/null 2>&1; then echo 'Unexpected database visibility'; exit 1; else echo 'PASS: frontend has no direct database DNS route'; fi"])
    database_ip = lab.run(["docker", "inspect", database, "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"]).stdout.strip()
    lab.run(["docker", "exec", front, "sh", "-c", "if nc -z -w 2 \"$1\" 3306; then echo 'Unexpected direct database access'; exit 1; else echo 'PASS: frontend TCP access to the database IP is blocked'; fi", "sh", database_ip])
    lab.run(["docker", "inspect", back, "--format", "{{range $name, $config := .NetworkSettings.Networks}}{{$name}}{{println}}{{end}}"])
    lab.observations.append("Three new networks: frontend-to-backend and backend-to-MySQL pass; frontend-to-database is isolated; backend has two networks.")
    site = lab.scratch / "site"
    site.mkdir()
    (site / "index.html").write_text("<h1>Hello students</h1>\n")
    bind, _ = lab.container("bind", "nginx:1.27-alpine", detached=True,
                           options=["-p", "127.0.0.1:0:80", "--mount", f"type=bind,src={site},dst=/usr/share/nginx/html,readonly"])
    binding = lab.run(["docker", "port", bind, "80/tcp"]).stdout.strip()
    url = "http://" + binding
    assert "Hello students</h1>" in lab.wait(["curl", "-fsS", url]).stdout
    if lab.browser_checkpoints:
        input(f"Live bind mount BEFORE screenshot: {url}. Press Enter after capture to update the file. ")
    before = lab.run(["docker", "inspect", bind, "--format", "{{.Id}} {{.RestartCount}}"]).stdout.strip()
    (site / "index.html").write_text("<h1>Hello students - updated live</h1>\n")
    lab.wait(["curl", "-fsS", url], expected="updated live")
    after = lab.run(["docker", "inspect", bind, "--format", "{{.Id}} {{.RestartCount}}"]).stdout.strip()
    assert before == after and before.endswith(" 0")
    if lab.browser_checkpoints:
        input(f"Live bind mount AFTER screenshot: {url}. Press Enter after capture to continue. ")
    lab.observations.append("Bind mount changed the HTTP response with the same container ID and zero restarts.")
    probe = lab.run(["docker", "run", "--rm", "--network", "host", "alpine:3.20", "sh", "-c",
                     "if nc -z -w 1 127.0.0.1 80; then exit 42; fi"], check=False)
    if probe.returncode == 42 or not free_port(80):
        lab.observations.append("BLOCKED: port 80 is unavailable on macOS or already has a Docker-host listener; host-mode Apache skipped without changing an existing service.")
        return
    assert probe.returncode == 0, "Host-network availability probe failed"
    marker = lab.scratch / "host-index.html"
    marker.write_text("<h1>Hello from isolated host-network Apache " + lab.prefix + "</h1>\n")
    host, _ = lab.container("host", "httpd:2.4-alpine", detached=True,
                           options=["--network", "host", "--mount", f"type=bind,src={marker},dst=/usr/local/apache2/htdocs/index.html,readonly"])
    lab.run(["docker", "inspect", host, "--format", "Network={{.HostConfig.NetworkMode}} PublishedPorts={{json .NetworkSettings.Ports}}"])
    lab.wait(["docker", "run", "--rm", "--network", "host", "alpine:3.20", "wget", "-qO-", "http://127.0.0.1:80"])
    mac = lab.run(["curl", "--fail", "--silent", "--show-error", "--max-time", "3", "http://127.0.0.1:80"], check=False)
    if mac.returncode == 0 and lab.prefix in mac.stdout:
        lab.observations.append("Host-mode Apache also reached directly on macOS port 80.")
    else:
        lab.observations.append("Host-mode Apache reached on port 80 in Docker's Linux host namespace. Direct macOS port 80 unavailable; Docker Desktop settings unchanged.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", choices=TOPICS, required=True)
    parser.add_argument("--pause", action="store_true", help="Pause on live results for a genuine Terminal screenshot before cleanup.")
    parser.add_argument("--browser-checkpoints", action="store_true", help="Pause before and after the bind-mount edit for genuine browser screenshots.")
    args = parser.parse_args()
    lab = Lab(args.topic)
    lab.browser_checkpoints = args.browser_checkpoints
    status = 0
    try:
        lab.say(f"Jaivardhan D. Rao | 24BCS10117 | LIVE {args.topic} coursework")
        lab.say("Started UTC: " + dt.datetime.now(dt.timezone.utc).isoformat())
        lab.say("Only new task-owned resources are used; no saved output is replayed.")
        globals()[args.topic.replace("-", "_")](lab)
        lab.say("\nLIVE OBSERVATIONS")
        for observation in lab.observations:
            lab.say("- " + observation)
        lab.say("Raw output: " + str(lab.path.relative_to(ROOT)))
        if args.pause:
            input("Capture this Terminal window now. Press Enter to clean up only this run's resources. ")
    except Exception as error:
        lab.say("\nFAILED: " + str(error))
        status = 1
    finally:
        lab.cleanup()
        lab.say("Cleanup finished for this run's exact container/network/image names and scratch directory.")
        lab.log.close()
    raise SystemExit(status)

if __name__ == "__main__":
    main()
