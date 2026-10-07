#!/usr/bin/env python3
"""Run only in the explicitly named disposable local cluster; record real output."""
import datetime, json, os, pathlib, shlex, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
CONTEXT = "devops-oct7"
NS = "devops-advanced"
MODE = sys.argv[1] if len(sys.argv)>1 else "storage"
LOGROOT = ROOT if MODE == "storage" else REPO / "kubernetes-troubleshooting"
(LOGROOT / "evidence").mkdir(exist_ok=True)
log = (LOGROOT / "evidence" / (MODE + "-run.txt")).open("w")
def record(text):
    print(text, flush=True); log.write(text + "\n"); log.flush()
def run(args, check=True):
    args = [str(x) for x in args]
    record("\n$ " + shlex.join(args))
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    record(p.stdout.rstrip()); record("exit="+str(p.returncode))
    if check and p.returncode: raise RuntimeError("command failed")
    return p.stdout

def k(*args, check=True):
    return run(["kubectl", "--context", CONTEXT, "-n", NS, *args], check=check)

def wait_reason(name, wanted, seconds=100):
    end=time.time()+seconds
    while time.time()<end:
        data=json.loads(k("get","pod",name,"-o","json"))
        statuses=data.get("status",{}).get("containerStatuses",[])
        reasons=[s.get("state",{}).get("waiting",{}).get("reason","") for s in statuses]
        if wanted in reasons: return
        time.sleep(4)
    raise RuntimeError("Did not observe "+wanted)

def replace(name):
    k("delete","pod","trouble-"+name,"--wait=true")
    k("apply","-f",REPO/"kubernetes-troubleshooting"/"scenarios"/(name+"-fixed.json"))
    k("wait","--for=condition=Ready","pod/trouble-"+name,"--timeout=120s")

record("Run at " + datetime.datetime.now(datetime.timezone.utc).isoformat())
record("Agent-operated local coursework lab. No external cluster or cloud resources used.")
actual=run(["kubectl","config","get-contexts",CONTEXT,"-o","name"]).strip()
if actual != CONTEXT: raise RuntimeError("Required isolated context is absent")
endpoint=run(["kubectl","config","view","--context",CONTEXT,"--minify","-o","jsonpath={.clusters[0].cluster.server}"]).strip()
if not endpoint.startswith(("https://127.0.0.1:","https://localhost:")): raise RuntimeError("Refusing non-local API endpoint")
run(["kubectl","--context",CONTEXT,"get","nodes","-o","wide"])
if MODE == "storage":
    k("apply","-f",ROOT/"mini-project")
    k("apply","-f",ROOT/"hpa.yml")
    k("rollout","status","deployment/advanced-web","--timeout=240s")
    k("get","pvc"); k("get","pv"); k("get","storageclass")
    old=json.loads(k("get","pods","-l","app=advanced-web","-o","json"))["items"][0]["metadata"]["name"]
    k("exec",old,"--","sh","-c","echo 'Session 13 persistent marker' > /data/student.txt; cat /data/student.txt")
    olduid=json.loads(k("get","pod",old,"-o","json"))["metadata"]["uid"]
    k("delete","pod",old,"--wait=true")
    time.sleep(3)
    k("rollout","status","deployment/advanced-web","--timeout=120s")
    k("wait","--for=condition=Ready","pod","-l","app=advanced-web","--timeout=120s")
    pods=json.loads(k("get","pods","-l","app=advanced-web","-o","json"))["items"]
    for pod in pods:
        assert pod["metadata"]["uid"] != olduid
        k("exec",pod["metadata"]["name"],"--","cat","/data/student.txt")
    k("apply","-f",ROOT/"01-kubernetes-volumes"/"examples.yaml")
    k("wait","--for=condition=Ready","pod/volume-examples","--timeout=120s")
    k("exec","volume-examples","--","sh","-c","cat /scratch/example /node/example; wget -q -O- http://advanced-web")
    k("get","hpa"); k("top","pods",check=False)
    k("apply","-f",ROOT/"load-generator.yaml")
    scaled=False
    try:
        for i in range(24):
            time.sleep(10)
            k("get","hpa"); k("top","pods",check=False)
            state=json.loads(k("get","deployment","advanced-web","-o","json"))
            k("get","pods","-l","app=advanced-web")
            if state.get("status",{}).get("readyReplicas",0)>2:
                scaled=True;break
        k("describe","hpa","advanced-web")
    finally:
        k("delete","job","advanced-load","--ignore-not-found=true")
    if not scaled: raise RuntimeError("HPA did not scale above two observed Ready replicas")
    # A readiness failure removes only the selected Pod from serving endpoints.
    pod=json.loads(k("get","pods","-l","app=advanced-web","-o","json"))["items"][0]["metadata"]["name"]
    k("exec",pod,"--","touch","/tmp/not-ready")
    time.sleep(12)
    k("get","pod",pod); k("get","endpointslices","-l","kubernetes.io/service-name=advanced-web","-o","yaml")
    k("exec",pod,"--","rm","/tmp/not-ready")
    k("wait","--for=condition=Ready","pod/"+pod,"--timeout=60s")
    for i in range(18):
        time.sleep(10)
        k("get","hpa");k("top","pods",check=False)
        state=json.loads(k("get","deployment","advanced-web","-o","json"))
        if state["spec"]["replicas"]==2: break
    k("get","pods","-o","wide");k("describe","hpa","advanced-web")
    state=json.loads(k("get","deployment","advanced-web","-o","json"))
    if state["spec"]["replicas"] != 2: raise RuntimeError("Scale-down to two replicas was not observed")
else:
    folder=REPO/"kubernetes-troubleshooting"
    k("apply","-f",folder/"mini-project.yaml")
    k("rollout","status","deployment/trouble-web","--timeout=180s")
    k("get","pods","-o","wide");k("explain","pod.spec.containers.resources");k("top","pods",check=False)
    for name in ["crash","image","pending","mount","config","dns","network"]:
        record("\nCASE: "+name)
        k("apply","-f",folder/"scenarios"/(name+"-broken.json"))
        if name=="crash":wait_reason("trouble-crash","CrashLoopBackOff")
        elif name=="image":
            wait_reason("trouble-image","ErrImagePull",120)
            k("get","pod","trouble-image");k("describe","pod","trouble-image")
            wait_reason("trouble-image","ImagePullBackOff",120)
        elif name in ["mount","config","pending"]:time.sleep(10)
        else:k("wait","--for=condition=Ready","pod/trouble-"+name,"--timeout=120s")
        k("get","pod","trouble-"+name);k("describe","pod","trouble-"+name)
        k("events","--for","pod/trouble-"+name)
        if name=="crash":k("logs","trouble-crash","--previous",check=False)
        if name=="dns":k("exec","trouble-dns","--","nslookup","trouble-web.devops-advanced.svc.cluster.local",check=False)
        if name=="network":
            ip=json.loads(k("get","pod","trouble-network","-o","json"))["status"]["podIP"]
            k("exec","volume-examples","--","wget","-T","3","-O-","http://"+ip+":8080",check=False)
            k("exec","trouble-network","--","python","-c","import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8080').status)")
        if name in ["mount", "config"]:
            k("apply","-f",folder/"scenarios"/(name+"-fixed.json"))
            k("wait","--for=condition=Ready","pod/trouble-"+name,"--timeout=120s")
            if name=="config":k("exec","trouble-config","--","printenv","MODE")
            else:k("exec","trouble-mount","--","cat","/config/MODE")
        else:replace(name)
        k("get","pod","trouble-"+name);k("logs","trouble-"+name)
        if name=="dns":k("exec","trouble-dns","--","nslookup","trouble-web.devops-advanced.svc.cluster.local")
        if name=="network":
            ip=json.loads(k("get","pod","trouble-network","-o","json"))["status"]["podIP"]
            k("exec","volume-examples","--","wget","-T","3","-O-","http://"+ip+":8080")
    record("\nCASE: Service selector mini-project")
    k("patch","service","trouble-web","--type=merge","-p",'{"spec":{"selector":{"app":"wrong-app"}}}')
    k("get","pods","-l","app=trouble-web","--show-labels")
    k("describe","service","trouble-web")
    k("get","endpointslices","-l","kubernetes.io/service-name=trouble-web","-o","yaml")
    k("exec","volume-examples","--","wget","-T","3","-O-","http://trouble-web",check=False)
    k("apply","-f",folder/"mini-project.yaml")
    time.sleep(3)
    k("get","endpointslices","-l","kubernetes.io/service-name=trouble-web","-o","yaml")
    k("exec","volume-examples","--","wget","-T","3","-O-","http://trouble-web")
    k("exec","deploy/trouble-web","--","sh","-c","wget -q -O- http://127.0.0.1")
    k("logs","deployment/trouble-web","--tail=8")
    k("get","events","--sort-by=.lastTimestamp")
record("\nCompleted all assertions for " + MODE)
