#!/usr/bin/env python3
import os, shutil, subprocess, time
from pathlib import Path

need=[]
if not shutil.which("keytool"):
    need.append("openjdk-17")
if not shutil.which("openssl"):
    need.append("openssl")

if not need:
    print("SIGNING_TOOLS_ALREADY_PRESENT")
    raise SystemExit(0)

lock=Path("/data/data/com.termux/files/usr/var/lib/apt/lists/lock")
for _ in range(120):
    holder=None
    try:
        r=subprocess.run(["fuser",str(lock)],text=True,capture_output=True,timeout=5)
        holder=(r.stdout or r.stderr).strip()
    except Exception:
        holder=""
    if not holder:
        break
    time.sleep(2)

cmd=["pkg","install","-y",*need]
r=subprocess.run(cmd,text=True,capture_output=True,timeout=900)
print("INSTALL_RETURN="+str(r.returncode))
print((r.stdout or "")[-4000:])
print((r.stderr or "")[-2000:])
raise SystemExit(r.returncode)
