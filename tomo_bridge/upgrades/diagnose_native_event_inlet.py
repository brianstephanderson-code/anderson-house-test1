#!/usr/bin/env python3
import socket, subprocess
from pathlib import Path

HOST="127.0.0.1"; PORT=8765
with socket.socket() as s:
    up = s.connect_ex((HOST,PORT)) == 0
print("INLET_PORT_UP="+str(up))

r=subprocess.run(["pgrep","-af","native_event_inlet_server.py"],text=True,capture_output=True)
print("INLET_PROCESS="+("yes" if r.stdout.strip() else "no"))

log=Path.home()/".tomo_private_events"/"inlet.log"
if log.exists():
    lines=log.read_text(encoding="utf-8",errors="replace").splitlines()[-40:]
    safe=[x for x in lines if "event" not in x.lower() or "Traceback" in x or "Error" in x or "Exception" in x]
    print("INLET_LOG_TAIL_BEGIN")
    for line in safe[-20:]:
        print(line[:500])
    print("INLET_LOG_TAIL_END")
else:
    print("INLET_LOG_MISSING")
