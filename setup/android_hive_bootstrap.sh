#!/data/data/com.termux/files/usr/bin/bash
set -eu

HIVE="${1:-}"
WORKER="${2:-}"

if [ -z "$HIVE" ] || [ -z "$WORKER" ]; then
  echo "Usage: bash setup/android_hive_bootstrap.sh HIVE workers/worker.py"
  exit 2
fi

REPO="$HOME/anderson-house-mailbox"
BOOTDIR="$HOME/.termux/boot"
BOOTFILE="$BOOTDIR/start-anderson-house.sh"
LOG="$HOME/$(echo "$HIVE" | tr '[:upper:]_' '[:lower:]-')-mailbox.log"

mkdir -p "$BOOTDIR"

cat > "$BOOTFILE" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sshd
cd "$REPO" || exit 1
if ! pgrep -f "python .*$WORKER" >/dev/null 2>&1; then
  nohup python "$WORKER" >> "$LOG" 2>&1 </dev/null &
fi
EOF

chmod +x "$BOOTFILE"

termux-wake-lock
sshd
cd "$REPO"
if ! pgrep -f "python .*$WORKER" >/dev/null 2>&1; then
  nohup python "$WORKER" >> "$LOG" 2>&1 </dev/null &
fi

echo "$HIVE READY"
echo "SSH door: ON"
echo "Worker: detached"
echo "Boot file: $BOOTFILE"
