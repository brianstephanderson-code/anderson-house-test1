#!/data/data/com.termux/files/usr/bin/bash
set -e

REPO="brianstephanderson-code/anderson-house-test1"
ROOT="$HOME/anderson-house-mailbox"

pkg install -y git gh python

if ! gh auth status >/dev/null 2>&1; then
    echo "ONE-TIME GITHUB AUTHORIZATION STARTING"
    gh auth login --hostname github.com --git-protocol https --web
fi

gh auth setup-git

if [ -d "$ROOT/.git" ]; then
    git -C "$ROOT" pull --rebase origin main
else
    gh repo clone "$REPO" "$ROOT"
fi

git -C "$ROOT" config user.name "S20 Worker"
git -C "$ROOT" config user.email "s20-worker@local"
chmod +x "$ROOT/workers/s20_mailbox.py"

echo "S20 GITHUB ROAD READY"
echo "NEXT: python $ROOT/workers/s20_mailbox.py"
