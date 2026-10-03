#!/usr/bin/env python3
import socket, subprocess, sys, time
from pathlib import Path

host="127.0.0.1"; port=8765
with socket.socket() as s:
    if s.connect_ex((host,port))==0:
        print("NATIVE_EVENT_INLET_ALREADY_RUNNING")
        raise SystemExit(0)

repo=Path.home()/"anderson-house-mailbox"
server=repo/"tomo_bridge"/"upgrades"/"native_event_inlet_server.py"
logdir=Path.home()/".tomo_private_events"
logdir.mkdir(parents=True,exist_ok=True)
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
time.sleep(1)
with socket.socket() as s:
    ok=s.connect_ex((host,port))==0
print("NATIVE_EVENT_INLET_STARTED" if ok else "NATIVE_EVENT_INLET_FAILED")
raise SystemExit(0 if ok else 1)
