#!/usr/bin/env python3
from pathlib import Path
import os, subprocess, textwrap

home = Path.home()
repo = home / "anderson-house-mailbox"
listener = repo / "tomo_bridge" / "termux_listener_v2.py"
logdir = home / ".tomo_bridge_v2"
logdir.mkdir(parents=True, exist_ok=True)
log = logdir / "listener.log"
inbox = repo / "tomo_bridge" / "inbox_v2"
inbox.mkdir(parents=True, exist_ok=True)

# Delay the restart so the currently running listener has time to record and push
# the result of this deployment command before it exits.
script = f"""#!/data/data/com.termux/files/usr/bin/bash
sleep 8
for p in $(pgrep -f '{listener}' 2>/dev/null || true); do
  [ "$p" = "$$" ] || kill "$p" 2>/dev/null || true
done
sleep 2
cd '{repo}' || exit 1
nohup python '{listener}' >>'{log}' 2>&1 &
sleep 2
cat > '{inbox}/bridge-v2-snapshot-loaded-20261003.command.json' <<'EOF'
{{
  "id": "bridge-v2-snapshot-loaded-20261003",
  "action": "android_whatsapp_message_snapshot",
  "timeout": 20
}}
EOF
"""
subprocess.Popen(
    ["/data/data/com.termux/files/usr/bin/bash", "-lc", script],
    cwd=repo,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True,
)
print("BRIDGE_V2_RESTART_SCHEDULED")
