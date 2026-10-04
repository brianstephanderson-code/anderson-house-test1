#!/usr/bin/env python3
import socket, subprocess, sys, time
from pathlib import Path

HOST="127.0.0.1"
PORT=8765
repo=Path.home()/"anderson-house-mailbox"
server=repo/"tomo_bridge"/"upgrades"/"native_event_inlet_server.py"
logdir=Path.home()/".tomo_private_events"
logdir.mkdir(parents=True,exist_ok=True)

# Stop only the known private localhost inlet process.
subprocess.run(
    ["pkill","-f",r"[n]ative_event_inlet_server.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=False,
)
time.sleep(0.5)

log=(logdir/"inlet.log").open("ab", buffering=0)
subprocess.Popen(
    [sys.executable,str(server)],
    cwd=repo,
    stdin=subprocess.DEVNULL,
    stdout=log,
    stderr=log,
    start_new_session=True,
    close_fds=True,
)
time.sleep(1.0)
with socket.socket() as s:
    ok=s.connect_ex((HOST,PORT))==0
print("NATIVE_EVENT_INLET_RESTARTED" if ok else "NATIVE_EVENT_INLET_RESTART_FAILED")
raise SystemExit(0 if ok else 1)
