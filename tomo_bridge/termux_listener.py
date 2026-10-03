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

CODEX_TERMUX = "codex-termux"
PNPM_BIN = Path.home() / ".local" / "share" / "pnpm" / "bin"

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

def safe_workdir(raw):
    if not raw:
        return REPO
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (REPO / p)
    p = p.resolve()
    allowed = [
        REPO.resolve(),
        (Path.home() / "downloads").resolve(),
    ]
    if not any(str(p).startswith(str(root) + os.sep) or p == root for root in allowed):
        raise ValueError("workdir outside allow-list")
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(str(p))
    return p

def codex_env():
    env = os.environ.copy()
    env["PATH"] = str(PNPM_BIN) + os.pathsep + env.get("PATH", "")
    return env

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

        elif action == "codex_exec":
            prompt = str(cmd.get("prompt", "")).strip()
            if not prompt:
                raise ValueError("codex_exec requires a non-empty prompt")
            if len(prompt) > 20000:
                raise ValueError("prompt too long")

            workdir = safe_workdir(cmd.get("workdir"))
            allow_write = bool(cmd.get("allow_write", False))
            if not allow_write:
                prompt = (
                    "READ-ONLY JOB. Do not create, edit, delete, move, rename, install, "
                    "or change files, apps, settings, services, network state, or system state. "
                    "Only inspect/read and report.\n\n" + prompt
                )

            args = [
                CODEX_TERMUX,
                "exec",
                "--skip-git-repo-check",
                "--ephemeral",
                "-s", "danger-full-access",
                "-c", 'approval_policy="never"',
                "-C", str(workdir),
                prompt,
            ]

            r = subprocess.run(
                args,
                cwd=workdir,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 900)),
                env=codex_env(),
            )
            result.update(
                ok=(r.returncode == 0),
                returncode=r.returncode,
                workdir=str(workdir),
                allow_write=allow_write,
                stdout=r.stdout[-30000:],
                stderr=r.stderr[-30000:],
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
    print("Actions: git_sync, run_repo_python, codex_exec, repo_status")

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
