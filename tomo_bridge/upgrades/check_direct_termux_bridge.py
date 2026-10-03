#!/usr/bin/env python3
import json, os, shutil, subprocess, platform
from pathlib import Path

def run(cmd):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=20)
        return {"ok": p.returncode == 0, "code": p.returncode, "out": p.stdout.strip()[-4000:], "err": p.stderr.strip()[-2000:]}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

checks = {
    "python": shutil.which("python"),
    "git": shutil.which("git"),
    "node": shutil.which("node"),
    "npm": shutil.which("npm"),
    "codex": shutil.which("codex"),
    "rish": shutil.which("rish"),
    "termux_open_url": shutil.which("termux-open-url"),
    "uname": run(["uname","-a"]),
    "android_release": run(["getprop","ro.build.version.release"]),
    "android_sdk": run(["getprop","ro.build.version.sdk"]),
    "model": run(["getprop","ro.product.model"]),
    "whoami": run(["whoami"]),
}
print(json.dumps(checks, indent=2, sort_keys=True))
