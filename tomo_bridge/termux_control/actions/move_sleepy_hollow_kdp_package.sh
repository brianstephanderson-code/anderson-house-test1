#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SRC="$HOME/downloads/Sleepy_Hollow_KDP_Production_Package.zip"
DEST_DIR="$HOME/downloads/Sleepy_Hollow"
DEST="$DEST_DIR/Sleepy_Hollow_KDP_Production_Package.zip"

mkdir -p "$DEST_DIR"

if [ -f "$DEST" ] && [ ! -f "$SRC" ]; then
  echo "ALREADY_IN_PLACE: $DEST"
  exit 0
fi

if [ ! -f "$SRC" ]; then
  echo "SOURCE_NOT_FOUND: $SRC" >&2
  exit 2
fi

if [ -e "$DEST" ]; then
  echo "DESTINATION_EXISTS: $DEST" >&2
  exit 3
fi

mv "$SRC" "$DEST"
echo "MOVED_OK: $DEST"
ls -lh "$DEST"
