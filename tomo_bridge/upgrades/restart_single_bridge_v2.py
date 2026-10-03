#!/usr/bin/env python3
from pathlib import Path
import subprocess
home=Path.home()
repo=home/"anderson-house-mailbox"
listener=repo/"tomo_bridge"/"termux_listener_v2.py"
logdir=home/".tomo_bridge_v2"
logdir.mkdir(parents=True,exist_ok=True)
log=logdir/"listener.log"
script=f"""#!/data/data/com.termux/files/usr/bin/bash
sleep 8
for p in $(pgrep -f 'termux_listener_v2.py' 2>/dev/null || true); do
  kill "$p" 2>/dev/null || true
done
sleep 2
cd '{repo}' || exit 1
nohup python '{listener}' >>'{log}' 2>&1 &
"""
subprocess.Popen(
  ["/data/data/com.termux/files/usr/bin/bash","-lc",script],
  cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True
)
print("SINGLE_V2_RESTART_SCHEDULED")
