#!/usr/bin/env python3
import json, os, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path.home() / "anderson-house-phys"
ROOT.mkdir(parents=True, exist_ok=True)
STATE = ROOT / "s20-state.json"
CANDIDATE = ROOT / "AH-PHYS-001.candidate.txt"
CRASH_MARK = ROOT / ".crashed-once"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Anderson-House-S20"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def post_json(url, obj):
    data = json.dumps(obj).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json","User-Agent":"Anderson-House-S20"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def worker(base):
    claim = get_json(base + "/claim")
    if claim.get("status") == "DONE":
        print("Already DONE at controller.")
        return 0
    if claim.get("status") != "CLAIMED":
        print("No claim:", claim)
        return 2

    m = claim["manifest"]
    if m.get("parcel_id") != "AH-PHYS-001" or m.get("destination") != "S20":
        print("AIKIDO STOP: wrong parcel or destination")
        return 3

    st = {
        "parcel_id": m["parcel_id"],
        "claim_gen": claim["claim_gen"],
        "control_gen": claim["control_gen"],
        "manifest_hash": m["manifest_hash"]
    }
    STATE.write_text(json.dumps(st, sort_keys=True))

    output = str(m["input"]).lower()
    CANDIDATE.write_text(output)

    if not CRASH_MARK.exists():
        CRASH_MARK.write_text("worker intentionally crashed after staging candidate\n")
        print("TEST: candidate created. Killing worker before receipt...")
        return 42

    saved = json.loads(STATE.read_text())
    output = CANDIDATE.read_text()
    request_id = f"S20-{saved['parcel_id']}-claim-{saved['claim_gen']}-stage"
    resp = post_json(base + "/stage", {
        "request_id": request_id,
        "parcel_id": saved["parcel_id"],
        "claim_gen": saved["claim_gen"],
        "control_gen": saved["control_gen"],
        "output": output
    })
    print("Controller response:", json.dumps(resp, sort_keys=True))
    return 0 if resp.get("status") in ("DONE","DONE_ALREADY") else 4


def supervisor(base):
    print("ANDERSON HOUSE — S20 PHYSICAL TEST")
    print("Starting worker #1...")
    rc = subprocess.call([sys.executable, __file__, "--worker", base])
    if rc == 42:
        print("Worker #1 is dead. Supervisor restarting it...")
        time.sleep(2)
        rc = subprocess.call([sys.executable, __file__, "--worker", base])
    status = get_json(base + "/status")
    print("Final ledger:", json.dumps(status, sort_keys=True))
    if rc == 0 and status.get("state") == "DONE":
        print("PASS: restart recovered; one official DONE exists.")
        return 0
    print("FAIL: inspect output above.")
    return 5


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--worker":
        sys.exit(worker(sys.argv[2].rstrip("/")))
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} http://MOTO-IP:8765")
        sys.exit(1)
    sys.exit(supervisor(sys.argv[1].rstrip("/")))
