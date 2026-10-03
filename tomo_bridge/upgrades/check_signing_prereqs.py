#!/usr/bin/env python3
import shutil, subprocess

def yesno(x): return "YES" if x else "NO"

gh=shutil.which("gh")
keytool=shutil.which("keytool")
print("GH_PRESENT="+yesno(gh))
print("KEYTOOL_PRESENT="+yesno(keytool))
if gh:
    r=subprocess.run([gh,"auth","status"],text=True,capture_output=True,timeout=20)
    print("GH_AUTH_OK="+yesno(r.returncode==0))
else:
    print("GH_AUTH_OK=NO")
