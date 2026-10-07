#!/usr/bin/env python3
"""Expose actual session-12 Ingress GET responses on temporary loopback ports.

The relay only supplies Host: devops.test, needed by the real Ingress rule. It
passes response bytes unchanged; it does not render logs or manufacture a page.
Stop with Ctrl+C. No Kubernetes objects, system hosts or shared forwards change.
"""
import argparse
from datetime import datetime, timezone
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import re
import selectors
import subprocess
import time
from urllib.parse import urlparse


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--kubeconfig", type=Path, required=True)
parser.add_argument("--context", choices=("devops-oct7",), required=True)
args = parser.parse_args()
environment = os.environ.copy()
environment["KUBECONFIG"] = str(args.kubeconfig.resolve())
base = ["kubectl", "--context", args.context, "--request-timeout=10s"]
server = subprocess.check_output(base + ["config", "view", "--minify", "-o", "jsonpath={.clusters[0].cluster.server}"],
                                 env=environment, text=True, timeout=15).strip()
if urlparse(server).scheme != "https" or urlparse(server).hostname not in ("127.0.0.1", "localhost", "::1"):
    parser.error("Refusing a non-loopback Kubernetes API")
command = base + ["-n", "ingress-nginx", "port-forward", "--address=127.0.0.1", "service/ingress-nginx-controller", ":80"]
forward = subprocess.Popen(command, env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
web = None
try:
    deadline = time.monotonic() + 15
    ingress_port = None
    with selectors.DefaultSelector() as selector:
        selector.register(forward.stdout, selectors.EVENT_READ)
        while time.monotonic() < deadline:
            if selector.select(timeout=1):
                line = forward.stdout.readline()
                if not line:
                    break
                print(line.rstrip(), flush=True)
                match = re.search(r"Forwarding from 127\.0\.0\.1:(\d+) ->", line)
                if match:
                    ingress_port = int(match.group(1))
                    break
            if forward.poll() is not None:
                break
    if ingress_port is None:
        raise RuntimeError("Own Ingress forward did not become ready")

    class Relay(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/", "/api/health"):
                self.send_error(404)
                return
            connection = http.client.HTTPConnection("127.0.0.1", ingress_port, timeout=5)
            try:
                # Never forward browser cookies, credentials, or arbitrary URLs.
                connection.request("GET", self.path, headers={"Host": "devops.test"})
                response = connection.getresponse()
                body = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", response.getheader("Content-Type", "application/octet-stream"))
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(body)
            except (OSError, http.client.HTTPException):
                self.send_error(502, "The actual local Ingress could not be reached")
            finally:
                connection.close()

    web = ThreadingHTTPServer(("127.0.0.1", 0), Relay)
    print("UTC: " + datetime.now(timezone.utc).isoformat(), flush=True)
    print("Context: devops-oct7; actual Ingress Host: devops.test", flush=True)
    print(f"BROWSER_URL=http://127.0.0.1:{web.server_port}", flush=True)
    print("GET / and /api/health only; actual response bytes are unchanged. Ctrl+C stops only this relay and its forward.", flush=True)
    web.serve_forever()
except KeyboardInterrupt:
    print("Stopping own temporary session-12 browser relay.", flush=True)
finally:
    if web is not None:
        web.server_close()
    if forward.poll() is None:
        forward.terminate()
    forward.wait(timeout=10)
    print("Own session-12 relay and Ingress forward stopped.", flush=True)
