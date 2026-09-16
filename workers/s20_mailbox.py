#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

ROOT = Path.home() / "anderson-house-mailbox"
JOBS = ROOT / "jobs"
RESULTS = ROOT / "results"
INTERVAL = 30


def run(*args, check=True):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)


def pull():
    run("git", "pull", "--rebase", "--autostash", "origin", "main")


def parse_job(path):
    data = {}
    for raw in path.read_text().splitlines():
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


def publish_result(job_id, function, status, output):
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"{job_id}.result"
    out.write_text(
        f"JOB_ID={job_id}\n"
        f"WORKER=S20\n"
        f"FUNCTION={function}\n"
        f"STATUS={status}\n"
        f"OUTPUT={output}\n"
    )

    run("git", "add", str(out.relative_to(ROOT)))
    changed = run("git", "diff", "--cached", "--quiet", check=False)
    if changed.returncode == 0:
        return

    run("git", "commit", "-m", f"S20 result {job_id}")
    run("git", "pull", "--rebase", "origin", "main")
    run("git", "push", "origin", "main")


def process_jobs():
    JOBS.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)

    for path in sorted(JOBS.glob("*.job")):
        job = parse_job(path)
        job_id = job.get("JOB_ID", path.stem)
        worker = job.get("WORKER", "")
        function = job.get("FUNCTION", "")

        if worker != "S20":
            continue
        if (RESULTS / f"{job_id}.result").exists():
            continue

        try:
            fn = FUNCTIONS[function]
            output = fn()
            publish_result(job_id, function, "DONE", output)
            print(f"DONE: {job_id} -> {output}", flush=True)
        except Exception as exc:
            publish_result(job_id, function or "UNKNOWN", "FAILED", str(exc).replace("\n", " "))
            print(f"FAILED: {job_id} -> {exc}", flush=True)


print("ANDERSON HOUSE — S20 MAILBOX")
print("Watching GitHub for jobs...", flush=True)

while True:
    try:
        pull()
        process_jobs()
    except Exception as exc:
        print(f"MAILBOX RETRY: {exc}", flush=True)
    time.sleep(INTERVAL)
