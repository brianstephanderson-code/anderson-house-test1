#!/data/data/com.termux/files/usr/bin/bash
set -e
echo "DEVICE=$(getprop ro.product.model 2>/dev/null || echo unknown)"
echo "ANDROID=$(getprop ro.build.version.release 2>/dev/null || echo unknown)"
echo "TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "UPTIME=$(uptime 2>/dev/null || true)"
echo "DISK="
df -h "$HOME" 2>/dev/null | tail -1 || true
echo "PYTHON=$(python --version 2>&1)"
echo "GIT=$(git --version 2>&1)"
