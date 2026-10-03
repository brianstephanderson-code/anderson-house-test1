#!/usr/bin/env python3
from pathlib import Path
import os, subprocess, sys, time

home=Path.home()
repo=home/"anderson-house-mailbox"
boot=home/".termux"/"boot"/"tomo_bridge.sh"
starter=repo/"tomo_bridge"/"upgrades"/"start_native_bridge_watchdog.py"

text=boot.read_text(encoding="utf-8")
line='python "$REPO/tomo_bridge/upgrades/start_native_bridge_watchdog.py" >>"$LOG_FILE" 2>&1 || true\n'
if "start_native_bridge_watchdog.py" not in text:
    marker='python "$REPO/tomo_bridge/upgrades/start_native_event_inlet.py" >>"$LOG_FILE" 2>&1 || true\n'
    text=text.replace(marker, marker+"\n"+line)
    boot.write_text(text,encoding="utf-8")
    boot.chmod(0o700)

r=subprocess.run([sys.executable,str(starter)],cwd=repo,text=True,capture_output=True,timeout=20)
print("BOOT_WATCHDOG_PRESENT="+("YES" if "start_native_bridge_watchdog.py" in boot.read_text(encoding="utf-8") else "NO"))
print("WATCHDOG_START="+(r.stdout.strip() or r.stderr.strip() or str(r.returncode)))
print("WATCHDOG_V4=GREEN" if r.returncode==0 else "WATCHDOG_V4=RED")
