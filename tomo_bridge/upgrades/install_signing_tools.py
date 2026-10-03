#!/usr/bin/env python3
import shutil, subprocess, sys

need=[]
if not shutil.which("keytool"):
    need.append("openjdk-17")
if not shutil.which("openssl"):
    need.append("openssl")

if not need:
    print("SIGNING_TOOLS_ALREADY_PRESENT")
    raise SystemExit(0)

cmd=["pkg","install","-y",*need]
r=subprocess.run(cmd,text=True,capture_output=True,timeout=900)
print("INSTALL_RETURN="+str(r.returncode))
print((r.stdout or "")[-4000:])
print((r.stderr or "")[-2000:])
raise SystemExit(r.returncode)
