#!/data/data/com.termux/files/usr/bin/python
import json, os, subprocess, time
from pathlib import Path

ROOT = Path.home() / "anderson-house-mailbox"
BASE = ROOT / "tomo_bridge" / "termux_control"
INBOX = BASE / "jobs" / "inbox"
DONE = BASE / "jobs" / "done"
RESULTS = BASE / "results"
ACTIONS = BASE / "actions"
POLL_SECONDS = 60

for p in (INBOX, DONE, RESULTS, ACTIONS):
    p.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT, timeout=900):
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)

def git_sync():
    r = run(["git","pull","--ff-only","origin","main"])
    return r.returncode, r.stdout + r.stderr

def git_publish(paths, message):
    run(["git","add",*paths])
    c = run(["git","commit","-m",message])
    if c.returncode not in (0,1):
        return c.returncode, c.stdout + c.stderr
    p = run(["git","push","origin","main"])
    return p.returncode, p.stdout + p.stderr

def safe_action(name):
    if not name or "/" in name or "\\" in name or name.startswith("."):
        return None
    p = ACTIONS / name
    if not p.exists() or not p.is_file():
        return None
    return p

while True:
    try:
        git_sync()
        for jobfile in sorted(INBOX.glob("*.json")):
            try:
                job = json.loads(jobfile.read_text())
                job_id = job.get("job_id", jobfile.stem)
                action = job.get("action")
                result = {
                    "job_id": job_id,
                    "action": action,
                    "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                if action == "heartbeat":
                    result.update({"ok": True, "stdout": "TERMUX_BRIDGE_GREEN"})
                elif action == "repo_sync":
                    rc, out = git_sync()
                    result.update({"ok": rc == 0, "stdout": out[-12000:]})
                elif action == "run_vetted":
                    script = safe_action(job.get("script"))
                    if script is None:
                        result.update({"ok": False, "error": "script_not_allowlisted"})
                    else:
                        r = run(["bash", str(script)], timeout=int(job.get("timeout",900)))
                        result.update({
                            "ok": r.returncode == 0,
                            "returncode": r.returncode,
                            "stdout": r.stdout[-12000:],
                            "stderr": r.stderr[-12000:]
                        })
                else:
                    result.update({"ok": False, "error": "unknown_action"})
                result["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                out = RESULTS / f"{job_id}.json"
                out.write_text(json.dumps(result, indent=2))
                target = DONE / jobfile.name
                jobfile.replace(target)
                rels = [str(out.relative_to(ROOT)), str(target.relative_to(ROOT))]
                git_publish(rels, f"Termux bridge result {job_id}")
            except Exception as e:
                err = RESULTS / f"{jobfile.stem}.error.json"
                err.write_text(json.dumps({"ok":False,"error":repr(e)}, indent=2))
                git_publish([str(err.relative_to(ROOT))], f"Termux bridge error {jobfile.stem}")
        time.sleep(POLL_SECONDS)
    except Exception:
        time.sleep(POLL_SECONDS)
