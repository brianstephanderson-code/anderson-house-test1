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
INTERVAL = 30
WORKER = "S20"
JOB_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


def gh(*args, check=True):
    return subprocess.run(
        ["gh", *args],
        text=True,
        capture_output=True,
        check=check,
    )


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


def battery():
    cap = Path("/sys/class/power_supply/battery/capacity").read_text().strip()
    status = Path("/sys/class/power_supply/battery/status").read_text().strip()
    return f"S20 battery: {cap}% — {status}"


FUNCTIONS = {
    "battery": battery,
}


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
    p = gh(
        "api", "--method", "PUT",
        f"{RESULTS_API}/{job_id}.result",
        "-f", f"message={WORKER} result {job_id}",
        "-f", f"content={encoded}",
        check=False,
    )
    if p.returncode != 0 and "already exists" not in (p.stderr + p.stdout).lower():
        raise RuntimeError((p.stderr or p.stdout).strip())


def fetch_job(name):
    item = gh_json("api", f"{JOBS_API}/{name}")
    raw = base64.b64decode(item["content"]).decode("utf-8")
    return parse_job(raw)


def list_jobs():
    listing = gh_json("api", JOBS_API)
    return sorted(
        item["name"]
        for item in listing
        if item.get("type") == "file" and item.get("name", "").endswith(".job")
    )


def process_once():
    for name in list_jobs():
        job = fetch_job(name)
        job_id = job.get("JOB_ID", Path(name).stem)
        worker = job.get("WORKER", "")
        function = job.get("FUNCTION", "")

        if worker != WORKER:
            continue
        if not JOB_ID_RE.fullmatch(job_id):
            print(f"QUARANTINE: invalid job id in {name}", flush=True)
            continue
        if result_exists(job_id):
            continue

        if function not in FUNCTIONS:
            publish_result(job_id, function or "UNKNOWN", "FAILED", "Function not allowed")
            print(f"FAILED: {job_id} -> function not allowed", flush=True)
            continue

        try:
            output = FUNCTIONS[function]()
            publish_result(job_id, function, "DONE", output)
            print(f"DONE: {job_id} -> {output}", flush=True)
        except Exception as exc:
            message = str(exc).replace("\n", " ")[:500]
            publish_result(job_id, function, "FAILED", message)
            print(f"FAILED: {job_id} -> {message}", flush=True)


print("ANDERSON HOUSE — S20 API AGENT")
print("Road: GitHub API <-> S20")
print("Allowed functions: " + ", ".join(sorted(FUNCTIONS)), flush=True)

while True:
    try:
        process_once()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"AGENT RETRY: {str(exc).replace(chr(10), ' ')[:500]}", flush=True)
    time.sleep(INTERVAL)
