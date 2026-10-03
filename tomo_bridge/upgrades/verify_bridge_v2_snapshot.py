#!/usr/bin/env python3
from pathlib import Path
import py_compile

repo = Path.home() / "anderson-house-mailbox"
listener = repo / "tomo_bridge" / "termux_listener_v2.py"
py_compile.compile(str(listener), doraise=True)
text = listener.read_text(encoding="utf-8")
required = [
    'elif action == "android_whatsapp_message_snapshot":',
    'encrypted_visible_whatsapp_snapshot',
    'plaintext_published=False',
]
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("MISSING: " + ", ".join(missing))
print("BRIDGE_V2_SNAPSHOT_VERIFY_OK")
