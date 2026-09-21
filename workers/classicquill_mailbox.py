#!/usr/bin/env python3
import base64
import json
import re
import subprocess
import time
from pathlib import Path

REPO = "brianstephanderson-code/anderson-house-test1"
JOBS_API = f"repos/{REPO}/contents/jobs"
RESULTS_API = f"repos/{REPO}/contents/results"
WORKER = "CLASSICQUILL"
INTERVAL = 15
TIMEOUT = 120

AH = Path(r"C:\AH")
INBOX = AH / "IN"
OUTBOX = AH / "OUT"
JOB_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
ALLOWED = {"uppercase", "lowercase", "wordcount", "campaign"}
CAMPAIGN_FUNCS = {"uppercase", "lowercase", "wordcount"}

def gh(*args, check=True):
    return subprocess.run(["gh", *args], text=True, capture_output=True, check=check)

def gh_json(*args):
    p = gh(*args)
    return json.loads(p.stdout)

def parse_job(text):
    data = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data

def result_exists(job_id):
    p = gh("api", f"{RESULTS_API}/{job_id}.result", check=False)
    return p.returncode == 0

def publish_result(job_id, function, status, output):
    text = (
        f"JOB_ID={job_id}\n"
        f"WORKER={WORKER}\n"
        f"FUNCTION={function}\n"
        f"STATUS={status}\n"
        f"OUTPUT={output}\n"
    )
    encoded = base64.b64encode(text.encode()).decode()
    p = gh("api", "--method", "PUT", f"{RESULTS_API}/{job_id}.result",
           "-f", f"message={WORKER} result {job_id}",
           "-f", f"content={encoded}", check=False)
    if p.returncode != 0 and "already exists" not in (p.stderr + p.stdout).lower():
        raise RuntimeError((p.stderr or p.stdout).strip())

def fetch_job(name):
    item = gh_json("api", f"{JOBS_API}/{name}")
    raw = base64.b64decode(item["content"]).decode("utf-8")
    return parse_job(raw)

def list_jobs():
    listing = gh_json("api", JOBS_API)
    return sorted(item["name"] for item in listing
                  if item.get("type") == "file" and item.get("name", "").endswith(".job"))

def run_local(job_id, function, data):
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    in_path = INBOX / f"{job_id}.json"
    out_path = OUTBOX / f"{job_id}.done.txt"
    if out_path.exists():
        return out_path.read_text(encoding="utf-8", errors="replace").strip()
    tmp = in_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"function": function, "data": data}), encoding="utf-8")
    tmp.replace(in_path)
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        if out_path.exists():
            return out_path.read_text(encoding="utf-8", errors="replace").strip()
        time.sleep(1)
    raise TimeoutError("Local worker timed out")

def apply_campaign_function(function, data):
    if function == "uppercase":
        return str(data).upper()
    if function == "lowercase":
        return str(data).lower()
    if function == "wordcount":
        return str(len(str(data).split()))
    raise ValueError(f"Campaign function not allowed: {function}")

def run_campaign(job):
    funcs = [x.strip() for x in job.get("STEPS", "uppercase,wordcount").split(",") if x.strip()]
    if not funcs or any(f not in CAMPAIGN_FUNCS for f in funcs):
        raise ValueError("Invalid campaign STEPS")
    current = job.get("DATA", "")
    max_hours = min(max(float(job.get("MAX_HOURS", "10")), 0.01), 16.0)
    max_cycles = min(max(int(job.get("MAX_CYCLES", "1000")), 1), 10000)
    sleep_seconds = min(max(float(job.get("SLEEP_SECONDS", "1")), 0.0), 60.0)
    stop_on_stable = job.get("STOP_ON_STABLE", "YES").upper() not in {"NO", "FALSE", "0"}
    started = time.time()
    deadline = started + max_hours * 3600
    cycle = 0
    last_trace = ""
    while cycle < max_cycles and time.time() < deadline:
        cycle += 1
        before = current
        for f in funcs:
            current = apply_campaign_function(f, current)
            last_trace = f"cycle={cycle};function={f};output={str(current)[:120]}"
        if stop_on_stable and current == before:
            return f"DONE_STABLE cycles={cycle} elapsed={round(time.time()-started,2)}s output={current} trace={last_trace}"
        if sleep_seconds:
            time.sleep(sleep_seconds)
    reason = "MAX_CYCLES" if cycle >= max_cycles else "MAX_HOURS"
    return f"DONE_{reason} cycles={cycle} elapsed={round(time.time()-started,2)}s output={current} trace={last_trace}"

def process_once():
    for name in list_jobs():
        job = fetch_job(name)
        job_id = job.get("JOB_ID", Path(name).stem)
        worker = job.get("WORKER", "")
        function = job.get("FUNCTION", "")
        data = job.get("DATA", "")
        if worker != WORKER:
            continue
        if not JOB_ID_RE.fullmatch(job_id):
            print(f"QUARANTINE: invalid job id in {name}", flush=True)
            continue
        if result_exists(job_id):
            continue
        if function not in ALLOWED:
            publish_result(job_id, function or "UNKNOWN", "FAILED", "Function not allowed")
            continue
        try:
            output = run_campaign(job) if function == "campaign" else run_local(job_id, function, data)
            publish_result(job_id, function, "DONE", output)
            print(f"DONE: {job_id} -> {output}", flush=True)
        except Exception as exc:
            message = str(exc).replace("\n", " ")[:500]
            publish_result(job_id, function, "FAILED", message)
            print(f"FAILED: {job_id} -> {message}", flush=True)

print("ANDERSON HOUSE — CLASSICQUILL MAILBOX")
print("Road: GitHub API <-> CLASSICQUILL")
print("Allowed functions: " + ", ".join(sorted(ALLOWED)), flush=True)
while True:
    try:
        process_once()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"MAILBOX RETRY: {str(exc).replace(chr(10), ' ')[:500]}", flush=True)
    time.sleep(INTERVAL)
