#!/usr/bin/env python3
import subprocess
r=subprocess.run(["sh","-lc","ps -A -o pid,comm,args | grep -E '(apt|dpkg)' | grep -v grep || true"],text=True,capture_output=True,timeout=15)
print(r.stdout.strip() or "NO_APT_DPKG_PROCESS")
