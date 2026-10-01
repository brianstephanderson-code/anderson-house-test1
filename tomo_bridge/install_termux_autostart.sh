#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="$HOME/anderson-house-mailbox"
BOOT_DIR="$HOME/.termux/boot"
RUN_DIR="$HOME/.tomo_bridge"
BOOT_FILE="$BOOT_DIR/tomo_bridge.sh"
LOG_FILE="$RUN_DIR/listener.log"
PID_FILE="$RUN_DIR/listener.pid"

mkdir -p "$BOOT_DIR" "$RUN_DIR"

if [ ! -d "$REPO/.git" ]; then
  echo "STOP: repo not found at $REPO"
  exit 1
fi

cd "$REPO"
git pull --ff-only origin main

cat > "$BOOT_FILE" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -u

REPO="$HOME/anderson-house-mailbox"
RUN_DIR="$HOME/.tomo_bridge"
LOG_FILE="$RUN_DIR/listener.log"
PID_FILE="$RUN_DIR/listener.pid"

mkdir -p "$RUN_DIR"

termux-wake-lock >/dev/null 2>&1 || true

if [ -f "$PID_FILE" ]; then
  oldpid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
    exit 0
  fi
fi

cd "$REPO" || exit 1
git pull --ff-only origin main >>"$LOG_FILE" 2>&1 || true

nohup python "$REPO/tomo_bridge/termux_listener.py" >>"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
EOF

chmod +x "$BOOT_FILE"

if [ -f "$PID_FILE" ]; then
  oldpid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
    kill "$oldpid" || true
    sleep 1
  fi
fi

termux-wake-lock >/dev/null 2>&1 || true

nohup python "$REPO/tomo_bridge/termux_listener.py" >>"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

sleep 2

echo
echo "========================================"
echo " TOMO BRIDGE AUTOSTART INSTALLED"
echo "========================================"
echo "PID: $(cat "$PID_FILE")"
echo "BOOT: $BOOT_FILE"
echo "LOG:  $LOG_FILE"
echo
echo "IMPORTANT: Termux:Boot app must be installed and opened once."
echo
echo "STATUS:"
if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "GREEN — listener is running"
else
  echo "RED — listener did not stay running"
  echo "Check: tail -50 $LOG_FILE"
  exit 1
fi
