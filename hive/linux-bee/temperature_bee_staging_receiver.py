"""Staging-only Moto poller: read-only probe, no production mailbox, no pushes.

Requires a one-time explicit installation on Moto. Not activated by GitHub commits.
"""
import json
import subprocess
import time
from pathlib import Path
from temperature_bee_command_guard import execute_probe, validate_command

REPO = Path.home() / "temperature-bee-staging-receiver"
BRANCH = "amigos-recovery-staging-20261009"
COMMAND_DIR = "hive/linux-bee/commands"
RESULT_DIR = Path.home() / "temperature-bee" / "staging-results"
SEEN = RESULT_DIR / "seen.jsonl"


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, text=True,
                          capture_output=True, timeout=60, check=True).stdout


def run_once():
    # Fetch only the isolated staging ref; never checkout or merge production.
    git("fetch", "--no-tags", "origin", f"refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
    paths = git("ls-tree", "-r", "--name-only", f"origin/{BRANCH}", COMMAND_DIR).splitlines()
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    seen = set()
    if SEEN.exists():
        for line in SEEN.read_text().splitlines():
            try:
                seen.add(json.loads(line)["id"])
            except (ValueError, KeyError, TypeError):
                pass
    count = 0
    for path in paths:
        if not path.endswith(".command.json"):
            continue
        raw = git("show", f"origin/{BRANCH}:{path}")
        try:
            command = validate_command(raw)
        except (ValueError, TypeError, KeyError):
            continue
        ident = command["id"]
        if ident in seen:
            continue
        # Persist a receipt before the probe to prevent duplicate execution.
        with SEEN.open("a") as f:
            f.write(json.dumps({"id": ident}) + "\n")
        seen.add(ident)
        result = execute_probe(command, lambda: "receiver-alive")
        (RESULT_DIR / (ident + ".result.json")).write_text(json.dumps(result, indent=2) + "\n")
        count += 1
    return count


if __name__ == "__main__":
    print(json.dumps({"probes_processed": run_once()}))
