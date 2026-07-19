#!/usr/bin/env python3
"""
Push src/data/city-content.json to GitHub via Contents API.
"""
import base64
import json
import os
import sys
import urllib.request

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(WEB, "src/data/city-content.json")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
REPO = "ReqTimeout/beriklan.co.id"
PATH = "src/data/city-content.json"


def get_sha():
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{PATH}",
        headers={"Authorization": f"token {GH_TOKEN}", "User-Agent": "sync"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("sha")


def put(content_b64, sha):
    body = json.dumps({
        "message": "chore(city-content): sync from D1 enrichment",
        "content": content_b64,
        "branch": "main",
    }).encode()
    if sha:
        body_dict = json.loads(body)
        body_dict["sha"] = sha
        body = json.dumps(body_dict).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{PATH}",
        data=body,
        headers={"Authorization": f"token {GH_TOKEN}", "Content-Type": "application/json", "User-Agent": "sync"},
        method="PUT",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    if not os.path.exists(CONTENT):
        print("no local file")
        return
    raw = open(CONTENT, "rb").read()
    if len(raw) > 900_000:
        print(f"WARN: file size {len(raw)} > 900KB — GitHub Contents API will reject (no content field)")
        print("Skipping GitHub push; city content will only be in D1 until split.")
        return
    b64 = base64.b64encode(raw).decode()
    try:
        sha = get_sha()
    except Exception as e:
        sha = None
        print(f"no existing sha: {e}")
    try:
        r = put(b64, sha)
        print(f"pushed: ok content len {len(raw)}")
    except urllib.error.HTTPError as e:
        print(f"push failed: {e.code} {e.read()[:200]}")


if __name__ == "__main__":
    main()
