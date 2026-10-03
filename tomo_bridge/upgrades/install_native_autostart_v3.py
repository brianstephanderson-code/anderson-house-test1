#!/usr/bin/env python3
from pathlib import Path
import os, socket, stat, subprocess, sys, time

home = Path.home()
repo = home / "anderson-house-mailbox"
boot_dir = home / ".termux" / "boot"
run_dir = home / ".tomo_bridge"
boot_file = boot_dir / "tomo_bridge.sh"
log_file = run_dir / "listener_v2.log"
pid_file = run_dir / "listener_v2.pid"

boot_dir.mkdir(parents=True, exist_ok=True)
run_dir.mkdir(parents=True, exist_ok=True)

script = r'''#!/data/data/com.termux/files/usr/bin/bash
set -u

REPO="$HOME/anderson-house-mailbox"
RUN_DIR="$HOME/.tomo_bridge"
LOG_FILE="$RUN_DIR/listener_v2.log"
PID_FILE="$RUN_DIR/listener_v2.pid"

mkdir -p "$RUN_DIR"
termux-wake-lock >/dev/null 2>&1 || true

cd "$REPO" || exit 1
git pull --ff-only origin main >>"$LOG_FILE" 2>&1 || true

# Ensure the private localhost event inlet is alive first.
python "$REPO/tomo_bridge/upgrades/start_native_event_inlet.py" >>"$LOG_FILE" 2>&1 || true

# Keep exactly one V2 listener process.
if [ -f "$PID_FILE" ]; then
  oldpid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
    exit 0
  fi
fi

nohup python "$REPO/tomo_bridge/termux_listener_v2.py" >>"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
'''

boot_file.write_text(script, encoding="utf-8")
boot_file.chmod(0o700)

# Ensure the native inlet is alive now, without disturbing the currently working listener.
starter = repo / "tomo_bridge" / "upgrades" / "start_native_event_inlet.py"
r = subprocess.run([sys.executable, str(starter)], cwd=repo, text=True, capture_output=True, timeout=20)

with socket.socket() as s:
    inlet_ok = (s.connect_ex(("127.0.0.1", 8765)) == 0)

print("BOOT_FILE=" + str(boot_file))
print("BOOT_V2_PRESENT=" + ("YES" if "termux_listener_v2.py" in boot_file.read_text() else "NO"))
print("BOOT_NATIVE_INLET_PRESENT=" + ("YES" if "start_native_event_inlet.py" in boot_file.read_text() else "NO"))
print("NATIVE_INLET_NOW=" + ("GREEN" if inlet_ok else "RED"))
print("STARTER=" + (r.stdout.strip() or r.stderr.strip() or "NO_OUTPUT"))
print("AUTOSTART_V3=GREEN" if inlet_ok else "AUTOSTART_V3=RED")
