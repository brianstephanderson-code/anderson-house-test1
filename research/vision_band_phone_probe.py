#!/usr/bin/env python3
import json, shutil, subprocess

result = {
    "termux_camera_photo": shutil.which("termux-camera-photo"),
    "termux_camera_info": shutil.which("termux-camera-info"),
}

if result["termux_camera_info"]:
    try:
        r = subprocess.run(
            ["termux-camera-info"],
            text=True,
            capture_output=True,
            timeout=20,
        )
        result["camera_info_returncode"] = r.returncode
        result["camera_info_stdout"] = r.stdout[-12000:]
        result["camera_info_stderr"] = r.stderr[-4000:]
    except Exception as e:
        result["camera_info_error"] = repr(e)

print(json.dumps(result, indent=2))
