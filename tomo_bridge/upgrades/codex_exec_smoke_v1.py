#!/usr/bin/env python3
import subprocess, json, os
from pathlib import Path

env=os.environ.copy()
env["PATH"]=str(Path.home()/".local/share/pnpm/bin")+":"+env.get("PATH","")
cmd=[
    "codex-termux","exec",
    "--skip-git-repo-check",
    "--ephemeral",
    "-s","danger-full-access",
    "-c",'approval_policy="never"',
    "Do not modify anything. Run pwd only and report the exact current directory."
]
p=subprocess.run(cmd,text=True,capture_output=True,timeout=180,env=env,cwd=Path.home()/"downloads")
print(json.dumps({
    "returncode":p.returncode,
    "stdout":p.stdout[-12000:],
    "stderr":p.stderr[-12000:]
},indent=2))
