#!/usr/bin/env python3
from pathlib import Path
import subprocess

rish=str(Path.home()/"bin"/"rish")
r=subprocess.run([rish,"-c","id"],text=True,capture_output=True,timeout=20)
print("returncode=",r.returncode)
print("stdout=",r.stdout.strip())
print("stderr=",r.stderr.strip())
