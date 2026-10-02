#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$HOME/anderson-house-mailbox"
BASE="$ROOT/tomo_bridge/termux_control"
BOOT="$HOME/.termux/boot"
mkdir -p "$BASE/jobs/inbox" "$BASE/jobs/done" "$BASE/results" "$BASE/actions" "$BOOT"

command -v python >/dev/null 2>&1 || pkg install -y python
command -v git >/dev/null 2>&1 || pkg install -y git

cat > "$BOOT/start_tomo_bridge.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock >/dev/null 2>&1 || true
cd "$HOME/anderson-house-mailbox" || exit 1
pkill -f "tomo_bridge/termux_control/worker.py" >/dev/null 2>&1 || true
nohup python "$HOME/anderson-house-mailbox/tomo_bridge/termux_control/worker.py"   >> "$HOME/anderson-house-mailbox/tomo_bridge/termux_control/bridge.log" 2>&1 &
EOF
chmod +x "$BOOT/start_tomo_bridge.sh"

pkill -f "tomo_bridge/termux_control/worker.py" >/dev/null 2>&1 || true
termux-wake-lock >/dev/null 2>&1 || true
nohup python "$BASE/worker.py" >> "$BASE/bridge.log" 2>&1 &

echo "TERMUX_BRIDGE_INSTALLED"
echo "PID: $(pgrep -f 'tomo_bridge/termux_control/worker.py' | head -1)"
