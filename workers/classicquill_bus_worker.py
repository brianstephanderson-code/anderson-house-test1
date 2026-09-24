#!/usr/bin/env python3
import subprocess
import time
import sys
import msvcrt
from pathlib import Path

from hive_peer_bus import process_bus

WORKER = "CLASSICQUILL"
ROOT = Path(__file__).resolve().parents[1]
INTERVAL = 15
SINGLETON_LOCK = ROOT / ".classicquill_crosstalk.lock"
_lock_handle = None

def acquire_singleton():
    global _lock_handle
    SINGLETON_LOCK.parent.mkdir(parents=True, exist_ok=True)
    _lock_handle = SINGLETON_LOCK.open("a+")
    _lock_handle.seek(0)
    if _lock_handle.tell() == 0:
        _lock_handle.write("0")
        _lock_handle.flush()
    _lock_handle.seek(0)
    try:
        msvcrt.locking(_lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print("CLASSICQUILL CROSSTALK ALREADY RUNNING — exiting duplicate.", flush=True)
        sys.exit(0)

def run(*args, check=True):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)

def sync():
    run("git", "fetch", "origin")
    r = run("git", "rebase", "origin/main", check=False)
    if r.returncode != 0:
        run("git", "rebase", "--abort", check=False)
        raise RuntimeError((r.stderr or r.stdout or "git rebase failed").strip())

acquire_singleton()
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
