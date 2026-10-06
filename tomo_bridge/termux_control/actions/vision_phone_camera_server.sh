#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "${HOME}/anderson-house-mailbox"

mkdir -p "${HOME}/anderson-house-mailbox/tomo_bridge/vision_phone_camera"

exec python warehouse/vision-band/phone_camera_adapter.py
