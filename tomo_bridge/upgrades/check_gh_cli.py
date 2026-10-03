#!/usr/bin/env python3
import shutil, subprocess
gh=shutil.which("gh")
print("GH="+("YES" if gh else "NO"))
if gh:
    r=subprocess.run([gh,"auth","status"],text=True,capture_output=True,timeout=20)
    print("GH_AUTH="+("YES" if r.returncode==0 else "NO"))
