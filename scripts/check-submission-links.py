#!/usr/bin/env python3
"""Check the 20 submitted main URLs and repository-relative documentation links.

The optional remote check reads public GitHub pages and compares commit-pinned
README bytes with this checkout. It never edits the repository or submits forms.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "jaivardhandrao/DevOps-Term-9"
TOPICS = [
    ("1–2", "linux-fundamentals"), ("3", "shell-scripting"),
    ("4", "networking"), ("5", "git-github"), ("6", "docker-apps"),
    ("7", "multi-stage-build"), ("8", "docker-networking"),
    ("9", "kubernetes-fundamentals"), ("10", "kubernetes-core-objects"),
    ("11", "kubernetes-services"), ("12", "kubernetes-ingress-configmaps-secrets"),
    ("13", "kubernetes-storage-hpa-probes"), ("14", "kubernetes-troubleshooting"),
    ("15", "helm"), ("16", "ci-cd"), ("17", "devsecops"),
    ("18", "terraform-s3-demo"), ("19", "cloud-terraform"),
    ("20", "monitoring-observability-gitops"), ("21", "final-devops-project"),
]
LINK = re.compile(r"(!?)\[[^\]]*\]\(([^)]+)\)")


def git_files(include_untracked):
    args = ["git", "ls-files", "--cached", "-z"]
    if include_untracked:
        args += ["--others", "--exclude-standard"]
    return set(filter(None, subprocess.check_output(args, cwd=ROOT).decode().split("\0")))


def local_check(include_untracked):
    files = git_files(include_untracked)
    submission = (ROOT / "SUBMISSION.md").read_text()
    errors, topics = [], []
    links_checked = 0
    image_files = set()
    for name in sorted(files):
        if not name.endswith(".md"):
            continue
        page = ROOT / name
        if not page.is_file():
            errors.append(f"Missing tracked Markdown: {name}")
            continue
        for image, raw in LINK.findall(page.read_text()):
            target = raw.split(' "', 1)[0].strip("<>")
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            path = unquote(target.split("#", 1)[0])
            if not path:
                continue
            resolved = (page.parent / path).resolve()
            if not resolved.is_relative_to(ROOT):
                errors.append(f"Link outside checkout: {name} -> {target}")
                continue
            relative = resolved.relative_to(ROOT).as_posix()
            if not resolved.exists():
                errors.append(f"Missing link: {name} -> {target}")
            elif resolved.is_file() and relative not in files:
                errors.append(f"Untracked link target: {name} -> {relative}")
            elif resolved.is_dir() and not any(f.startswith(relative + "/") for f in files):
                errors.append(f"Directory has no tracked files: {name} -> {relative}")
            links_checked += 1
            if image:
                image_files.add(relative)
    for session, folder in TOPICS:
        path = f"{folder}/README.md"
        url = f"https://github.com/{REPOSITORY}/blob/main/{path}"
        if path not in files or not (ROOT / path).is_file():
            errors.append(f"Submitted README missing: {path}")
            continue
        if url not in submission:
            errors.append(f"Submitted main URL missing from map: {url}")
        images = [target for image, target in LINK.findall((ROOT / path).read_text()) if image]
        topics.append({"session": session, "path": path, "url": url, "inline_images": len(images)})
    return {"utc": datetime.now(timezone.utc).isoformat(), "submitted_topics": topics,
            "topics_with_inline_images": sum(bool(t["inline_images"]) for t in topics),
            "relative_links_checked": links_checked,
            "distinct_inline_image_files": sorted(image_files), "errors": errors}


def fetch(url):
    return subprocess.check_output(
        ["curl", "--fail", "--location", "--silent", "--show-error",
         "--connect-timeout", "15", "--max-time", "60", "--retry", "2", url],
        cwd=ROOT, stderr=subprocess.PIPE)


def remote_check(topic, ref):
    try:
        page = fetch(topic["url"])
        if b"DevOps-Term-9" not in page:
            raise ValueError("GitHub page did not identify the expected repository")
        raw = fetch(f"https://raw.githubusercontent.com/{REPOSITORY}/{ref}/{topic['path']}")
        if raw != (ROOT / topic["path"]).read_bytes():
            raise ValueError(f"README differs from remote commit {ref}")
        return {"url": topic["url"], "http_read": "passed", "commit_bytes_match": True}
    except (subprocess.CalledProcessError, ValueError) as exc:
        return {"url": topic["url"], "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-untracked", action="store_true", help="Pre-commit audit of new evidence")
    parser.add_argument("--remote-ref", help="Also check public main URLs and compare README bytes at this immutable commit")
    args = parser.parse_args()
    if args.remote_ref and not re.fullmatch(r"[a-fA-F0-9]{40}", args.remote_ref):
        parser.error("--remote-ref requires a full immutable commit SHA")
    report = local_check(args.include_untracked)
    if args.remote_ref:
        with ThreadPoolExecutor(max_workers=4) as pool:
            report["remote"] = list(pool.map(lambda topic: remote_check(topic, args.remote_ref), report["submitted_topics"]))
        report["errors"] += [result["error"] for result in report["remote"] if "error" in result]
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return bool(report["errors"])


if __name__ == "__main__":
    raise SystemExit(main())
