#!/usr/bin/env python3
import os, socket, subprocess, sys, time
from pathlib import Path

HOME=Path.home()
REPO=HOME/"anderson-house-mailbox"
RUN=HOME/".tomo_bridge"
LOG=RUN/"watchdog.log"
PID_FILE=RUN/"listener_v2.pid"
STARTER=REPO/"tomo_bridge"/"upgrades"/"start_native_event_inlet.py"
LISTENER=REPO/"tomo_bridge"/"termux_listener_v2.py"

RUN.mkdir(parents=True, exist_ok=True)

def log(msg):
    stamp=time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG.open("a",encoding="utf-8") as f:
        f.write(f"{stamp} {msg}\n")

def port_up():
    try:
        with socket.create_connection(("127.0.0.1",8765),timeout=1):
            return True
    except OSError:
        return False

def listener_up():
    try:
        pid=int(PID_FILE.read_text().strip())
        os.kill(pid,0)
        return True
    except Exception:
        return False

def start_inlet():
    r=subprocess.run([sys.executable,str(STARTER)],cwd=REPO,text=True,capture_output=True,timeout=20)
    log("inlet restart: "+(r.stdout.strip() or r.stderr.strip() or str(r.returncode)))

def start_listener():
    out=(RUN/"listener_v2.log").open("ab",buffering=0)
    p=subprocess.Popen([sys.executable,str(LISTENER)],cwd=REPO,stdin=subprocess.DEVNULL,stdout=out,stderr=out,start_new_session=True,close_fds=True)
    PID_FILE.write_text(str(p.pid)+"\n")
    log(f"listener restart pid={p.pid}")

log("watchdog started")
while True:
    try:
        if not port_up():
            start_inlet()
        if not listener_up():
            start_listener()
    except Exception as e:
        log("watchdog error: "+repr(e))
    time.sleep(60)
