#!/usr/bin/env python3
import json, subprocess, shutil, time

def run(cmd, timeout=6):
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
        return {"rc":p.returncode,"out":(p.stdout or "").strip()[:8000],"err":(p.stderr or "").strip()[:4000]}
    except Exception as e:
        return {"error":repr(e)}
d={}
d["utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
d["pm_termux_packages"]=run(["bash","-lc","pm list packages 2>&1 | grep -E 'com\\.termux(\\.api)?' || true"])
d["termux_info"]=run(["bash","-lc","termux-info 2>&1 | head -120"])
d["api_binary"]=shutil.which("termux-battery-status")
d["api_pkg"]=run(["bash","-lc","pkg list-installed 2>/dev/null | grep '^termux-api/' || true"])
d["battery_call_3s"]=run(["bash","-lc","timeout 3 termux-battery-status 2>&1"],5)
d["dumpsys_battery"]=run(["bash","-lc","dumpsys battery 2>&1 | head -80"])
print(json.dumps(d,indent=2,sort_keys=True))
