#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "VISION_PHONE_CAMERA_PROBE"
if command -v termux-camera-photo >/dev/null 2>&1; then
  echo "termux_camera_photo=present"
  termux-camera-info 2>/dev/null || true
  exit 0
else
  echo "termux_camera_photo=missing"
  echo "Camera substitute needs Termux:API + termux-api package, or the Android device-agent camera path."
  exit 3
fi
