#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${HOME}/anderson-house-mailbox"
cd "${ROOT}"

python warehouse/vision-band/test_endpoint_replay.py
