#!/data/data/com.termux/files/usr/bin/bash
set -e

REPO="brianstephanderson-code/anderson-house-test1"
BASE="$HOME/Anderson_House"
WORKERS="$BASE/Workers"
LOGS="$BASE/Logs"
BOOT="$HOME/.termux/boot"
AGENT="$WORKERS/s20_api_agent.py"
BOOTFILE="$BOOT/start-s20-api-agent"

command -v gh >/dev/null || { echo "STOP: gh not installed"; exit 1; }
command -v python >/dev/null || { echo "STOP: python not installed"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "STOP: GitHub authorization missing"; exit 1; }

mkdir -p "$WORKERS" "$LOGS" "$BOOT"

gh api \
  -H "Accept: application/vnd.github.raw+json" \
  "repos/$REPO/contents/workers/s20_api_agent.py" > "$AGENT"
chmod 700 "$AGENT"

cat > "$BOOTFILE" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
mkdir -p "$HOME/Anderson_House/Logs"
if ! pgrep -f 's20_api_agent.py' >/dev/null 2>&1; then
  nohup python "$HOME/Anderson_House/Workers/s20_api_agent.py" \
    >> "$HOME/Anderson_House/Logs/s20_api_agent.log" 2>&1 &
fi
EOF
chmod 700 "$BOOTFILE"

pkill -f 's20_api_agent.py' >/dev/null 2>&1 || true
termux-wake-lock >/dev/null 2>&1 || true
nohup python "$AGENT" >> "$LOGS/s20_api_agent.log" 2>&1 &
sleep 3

if pgrep -f 's20_api_agent.py' >/dev/null 2>&1; then
  echo "S20 API AGENT: RUNNING"
  echo "LOG: $LOGS/s20_api_agent.log"
  echo "BOOT: ENABLED"
else
  echo "S20 API AGENT: FAILED TO START"
  echo "CHECK: $LOGS/s20_api_agent.log"
  exit 1
fi
