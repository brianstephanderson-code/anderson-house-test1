from pathlib import Path
import os, socket, subprocess, json

home = Path.home()
event_log = home / ".tomo_private_events" / "events.jsonl"

def running(pattern):
    r = subprocess.run(["pgrep","-f",pattern], capture_output=True, text=True)
    return r.returncode == 0

def port_open(host, port):
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()

event_lines = 0
if event_log.exists():
    try:
        with event_log.open("rb") as f:
            event_lines = sum(1 for _ in f)
    except Exception:
        event_lines = -1

status = {
    "v2_listener": running("termux_listener_v2.py"),
    "native_inlet": running("native_event_inlet_server.py"),
    "watchdog": running("native_bridge_watchdog.py"),
    "localhost_8765": port_open("127.0.0.1", 8765),
    "event_log_exists": event_log.exists(),
    "event_log_lines": event_lines,
}
status["green"] = all([
    status["v2_listener"],
    status["native_inlet"],
    status["watchdog"],
    status["localhost_8765"],
    status["event_log_exists"],
])
print(json.dumps(status, sort_keys=True))
