#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "${HOME}/anderson-house-mailbox"
python warehouse/vision-band/vision_band_action.py status
