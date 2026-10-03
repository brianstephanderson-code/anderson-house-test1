#!/usr/bin/env python3
import os, subprocess, sys
from pathlib import Path

home=Path.home()
repo=home/"anderson-house-mailbox"
run=home/".tomo_bridge"
run.mkdir(parents=True,exist_ok=True)
pid_file=run/"watchdog.pid"
log_file=run/"watchdog.log"
watchdog=repo/"tomo_bridge"/"upgrades"/"native_bridge_watchdog.py"

try:
    pid=int(pid_file.read_text().strip())
    os.kill(pid,0)
    print("WATCHDOG_ALREADY_RUNNING")
    raise SystemExit(0)
except Exception:
    pass

out=log_file.open("ab",buffering=0)
p=subprocess.Popen([sys.executable,str(watchdog)],cwd=repo,stdin=subprocess.DEVNULL,stdout=out,stderr=out,start_new_session=True,close_fds=True)
pid_file.write_text(str(p.pid)+"\n")
print("WATCHDOG_STARTED="+str(p.pid))
