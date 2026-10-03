#!/usr/bin/env python3
import subprocess, json, os
from pathlib import Path

cmd = ["codex-termux", "exec", "--help"]
env = os.environ.copy()
env["PATH"] = str(Path.home()/".local/share/pnpm/bin") + ":" + env.get("PATH","")
p = subprocess.run(cmd, text=True, capture_output=True, timeout=60, env=env)
print(json.dumps({
  "returncode": p.returncode,
  "stdout": p.stdout,
  "stderr": p.stderr
}, indent=2))
