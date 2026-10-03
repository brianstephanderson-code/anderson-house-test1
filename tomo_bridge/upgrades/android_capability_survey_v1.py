#!/usr/bin/env python3
import json, subprocess
from pathlib import Path

RISH = str(Path.home() / "bin" / "rish")

checks = {
    "identity": "id",
    "android_release": "getprop ro.build.version.release",
    "android_sdk": "getprop ro.build.version.sdk",
    "model": "getprop ro.product.model",
    "manufacturer": "getprop ro.product.manufacturer",
    "battery": "dumpsys battery | head -30",
    "display": "dumpsys power | grep -E 'Display Power|mWakefulness|Wakefulness' | head -20",
    "network": "dumpsys connectivity | head -60",
    "storage": "df -h /data /sdcard 2>/dev/null | head -20",
    "packages_count": "pm list packages | wc -l",
}

out = {"ok": True, "checks": {}}
for name, cmd in checks.items():
    try:
        p = subprocess.run(
            [RISH, "-c", cmd],
            text=True,
            capture_output=True,
            timeout=30,
        )
        out["checks"][name] = {
            "returncode": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
        if p.returncode != 0:
            out["ok"] = False
    except Exception as e:
        out["checks"][name] = {"error": f"{type(e).__name__}: {e}"}
        out["ok"] = False

print(json.dumps(out, indent=2))
