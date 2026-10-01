#!/usr/bin/env python3
import json, os, subprocess, time
from pathlib import Path

REPO = Path.home() / "anderson-house-mailbox"
INBOX = REPO / "tomo_bridge" / "inbox"
OUTBOX = REPO / "tomo_bridge" / "outbox"
DONE = REPO / "tomo_bridge" / "archive"
POLL_SECONDS = 60

ALLOWED_ROOTS = [
    (REPO / "tomo_bridge" / "upgrades").resolve(),
    (REPO / "research").resolve(),
    (REPO / "search-universe").resolve(),
]

def git(*args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=check,
    )

def safe_python_path(raw):
    p = (REPO / raw).resolve()
    if p.suffix != ".py":
        raise ValueError("only .py files are allowed")
    if not any(str(p).startswith(str(root) + os.sep) or p == root for root in ALLOWED_ROOTS):
        raise ValueError("path outside allow-list")
    if not p.exists():
        raise FileNotFoundError(str(p))
    return p

def write_result(cmd_id, result):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    path = OUTBOX / f"{cmd_id}.result.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path

def archive_command(path):
    DONE.mkdir(parents=True, exist_ok=True)
    target = DONE / path.name
    path.replace(target)
    return target

def process(path):
    cmd = json.loads(path.read_text())
    cmd_id = cmd.get("id") or path.stem
    action = cmd.get("action")
    result = {"id": cmd_id, "action": action, "ok": False}

    try:
        if action == "git_sync":
            r = git("pull", "--ff-only", "origin", "main")
            result.update(ok=True, stdout=r.stdout, stderr=r.stderr)

        elif action == "run_repo_python":
            script = safe_python_path(cmd["path"])
            args = [str(x) for x in cmd.get("args", [])]
            r = subprocess.run(
                ["python", str(script), *args],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 900)),
            )
            result.update(
                ok=(r.returncode == 0),
                returncode=r.returncode,
                stdout=r.stdout[-20000:],
                stderr=r.stderr[-20000:],
            )

        elif action == "repo_status":
            r = git("status", "--short")
            result.update(ok=True, stdout=r.stdout, stderr=r.stderr)

        else:
            raise ValueError(f"action not allowed: {action}")

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    write_result(cmd_id, result)
    archive_command(path)

    git("add", "tomo_bridge/outbox", "tomo_bridge/archive", check=False)
    git("commit", "-m", f"Termux result: {cmd_id}", check=False)
    git("push", "origin", "main", check=False)

def main():
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)

    print("TOMO BRIDGE — TERMUX LISTENER")
    print(f"Repo: {REPO}")
    print(f"Polling every {POLL_SECONDS}s")

    while True:
        try:
            git("pull", "--ff-only", "origin", "main", check=False)
            for path in sorted(INBOX.glob("*.command.json")):
                process(path)
        except Exception as e:
            print("listener error:", e)
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
