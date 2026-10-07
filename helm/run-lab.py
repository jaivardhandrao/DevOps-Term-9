#!/usr/bin/env python3
"""Helm lifecycle practice against the dedicated local lab context only."""
import datetime, json, os, pathlib, shlex, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parent
RUNTIME=ROOT.parent.parent/".runtime"
HELM=os.environ.get("HELM",str(RUNTIME/"bin"/"helm"))
os.environ["HELM_CACHE_HOME"]=str(RUNTIME/"helm"/"cache")
os.environ["HELM_CONFIG_HOME"]=str(RUNTIME/"helm"/"config")
os.environ["HELM_DATA_HOME"]=str(RUNTIME/"helm"/"data")
NS="devops-helm"
(ROOT/"evidence").mkdir(exist_ok=True)
log=(ROOT/"evidence"/"helm-run.txt").open("w")
def record(t):
    print(t,flush=True);log.write(t+"\n");log.flush()
def run(args,check=True):
    args=[str(x) for x in args];record("\n$ "+shlex.join(args))
    p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    record(p.stdout.rstrip());record("exit="+str(p.returncode))
    if check and p.returncode:raise RuntimeError("Command failed")
    return p.stdout

def h(*args,check=True):return run([HELM,"--kube-context","devops-oct7","-n",NS,*args],check)
def k(*args,check=True):return run(["kubectl","--context","devops-oct7","-n",NS,*args],check)
def verify():
    k("get","pods","-o","wide")
    k("get","service","notes-notes")
    k("exec","deployment/notes-notes","--","sh","-c","printenv APP_NAME ENVIRONMENT; wget -q -O- http://notes-notes")
record("Run at "+datetime.datetime.now(datetime.timezone.utc).isoformat())
record("Agent-operated disposable local Helm lab; no cloud deployment.")
assert run(["kubectl","config","get-contexts","devops-oct7","-o","name"]).strip()=="devops-oct7"
endpoint=run(["kubectl","config","view","--context","devops-oct7","--minify","-o","jsonpath={.clusters[0].cluster.server}"]).strip()
assert endpoint.startswith(("https://127.0.0.1:","https://localhost:"))
h("version","--short")
# Practice create in scratch; the submitted hand-authored chart is intentionally smaller.
scratch=RUNTIME/"helm"/"created-chart"
if scratch.exists():raise RuntimeError("Scratch chart already exists; choose a fresh path")
h("create",scratch)
h("lint",ROOT/"notes-chart")
h("template","notes",ROOT/"notes-chart")
h("repo","add","ingress-nginx","https://kubernetes.github.io/ingress-nginx")
h("repo","update")
h("repo","list")
h("search","repo","ingress-nginx",check=True)
h("install","notes",ROOT/"notes-chart","--create-namespace","--wait","--timeout","180s")
h("list");h("status","notes");h("get","values","notes","--all");h("get","manifest","notes")
verify()
h("upgrade","notes",ROOT/"notes-chart","-f",ROOT/"notes-chart"/"values-prod.yaml","--wait","--timeout","180s")
verify()
# Deliberately unsuccessful image rollout is kept visible and then rolled back.
h("upgrade","notes",ROOT/"notes-chart","-f",ROOT/"notes-chart"/"values-prod.yaml","--set","image.tag=devops-intentionally-missing")
for _ in range(20):
    time.sleep(4)
    data=json.loads(k("get","pods","-l","app.kubernetes.io/instance=notes","-o","json"))
    reasons=[c.get("state",{}).get("waiting",{}).get("reason","") for p in data["items"] for c in p.get("status",{}).get("containerStatuses",[])]
    if "ImagePullBackOff" in reasons or "ErrImagePull" in reasons:break
else:raise RuntimeError("Bad image failure was not observed")
k("get","pods");k("events","--types=Warning")
h("history","notes")
h("rollback","notes","2","--wait","--timeout","180s")
verify();h("history","notes")
h("uninstall","notes","--wait","--timeout","120s")
h("list");k("get","deployment/notes-notes","service/notes-notes","configmap/notes-config","--ignore-not-found=true")
# Keep a working review release after demonstrating uninstall.
h("install","notes",ROOT/"notes-chart","--wait","--timeout","180s")
verify()
record("\nCompleted install, two upgrades, observed failure, rollback, uninstall and review reinstall.")
