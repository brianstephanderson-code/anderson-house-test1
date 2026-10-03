#!/usr/bin/env python3
import subprocess
r=subprocess.run(["ps","-ef"],text=True,capture_output=True)
for line in r.stdout.splitlines():
    if "termux_listener_v2.py" in line or "termux_listener.py" in line:
        print(line)
