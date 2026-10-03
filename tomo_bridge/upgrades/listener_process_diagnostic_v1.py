#!/usr/bin/env python3
import subprocess, json, hashlib
from pathlib import Path

listener = Path.home()/"anderson-house-mailbox"/"tomo_bridge"/"termux_listener.py"
text = listener.read_text(errors="replace") if listener.exists() else ""
ps = subprocess.run(["ps","-A","-o","PID,PPID,ARGS"], text=True, capture_output=True)
lines = [ln for ln in ps.stdout.splitlines() if "termux_listener.py" in ln or "python" in ln]
print(json.dumps({
  "listener_exists": listener.exists(),
  "listener_sha256": hashlib.sha256(text.encode()).hexdigest() if text else None,
  "has_codex_exec_branch": 'elif action == "codex_exec":' in text,
  "processes": lines,
}, indent=2))
