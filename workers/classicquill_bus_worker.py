#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

from hive_peer_bus import process_bus

WORKER = "CLASSICQUILL"
ROOT = Path(__file__).resolve().parents[1]
INTERVAL = 15

def run(*args, check=True):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)

def sync():
    run("git", "fetch", "origin")
    r = run("git", "rebase", "origin/main", check=False)
    if r.returncode != 0:
        run("git", "rebase", "--abort", check=False)
        raise RuntimeError((r.stderr or r.stdout or "git rebase failed").strip())

print("ANDERSON HOUSE — CLASSICQUILL CROSSTALK WORKER", flush=True)
print("Watching GitHub over SSH...", flush=True)

while True:
    try:
        sync()
        made = process_bus(WORKER, ROOT)
        if made:
            print(f"CROSSTALK ACKS={made}", flush=True)
    except Exception as exc:
        print(f"CROSSTALK RETRY: {exc}", flush=True)
    time.sleep(INTERVAL)
