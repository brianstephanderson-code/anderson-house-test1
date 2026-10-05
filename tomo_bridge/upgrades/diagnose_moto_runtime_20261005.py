#!/usr/bin/env python3
import json, os, shutil, subprocess, time
from pathlib import Path

def run(cmd):
    try:
        p=subprocess.run(cmd, text=True, capture_output=True, timeout=10)
        return {"rc":p.returncode,"out":(p.stdout or "").strip()[:4000],"err":(p.stderr or "").strip()[:2000]}
    except Exception as e:
        return {"error":repr(e)}

def read(p):
    try:return Path(p).read_text().strip()
    except Exception as e:return "ERR:"+type(e).__name__

data={}
data["time_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
data["pid"]=os.getpid()
data["sys_capacity"]=read("/sys/class/power_supply/battery/capacity")
data["sys_status"]=read("/sys/class/power_supply/battery/status")
data["sys_temp"]=read("/sys/class/power_supply/battery/temp")
data["termux_battery_status_path"]=shutil.which("termux-battery-status")
if data["termux_battery_status_path"]:
    data["termux_battery_status"]=run(["termux-battery-status"])
data["termux_api_pkg_hint"]=run(["bash","-lc","command -v termux-battery-status || true; pkg list-installed 2>/dev/null | grep -E '^termux-api/' || true"])
data["listener_procs"]=run(["bash","-lc","ps -ef | grep -E 'termux_listener_v2.py|moto_local_mailbox.py' | grep -v grep || true"])
data["proc_uptime"]=run(["bash","-lc","uptime || true"])
print(json.dumps(data, indent=2, sort_keys=True))
