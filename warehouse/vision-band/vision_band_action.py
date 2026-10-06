#!/usr/bin/env python3
import json, os, sys, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from vision_band_client import VisionBandClient

BASE = os.environ.get("VISION_BAND_URL", "http://127.0.0.1:8787")
client = VisionBandClient(BASE, timeout=float(os.environ.get("VISION_BAND_TIMEOUT","5")))

def out(obj):
    print(json.dumps(obj, indent=2, sort_keys=True))

def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: vision_band_action.py status|parked|active|capture [note]")

    cmd = sys.argv[1].lower()

    if cmd == "status":
        code, body = client.status()
        out({"http":code, **body})
        raise SystemExit(0 if code == 200 else 1)

    if cmd in ("parked","active"):
        code, body = client.set_mode(cmd)
        out({"http":code, **body})
        raise SystemExit(0 if code == 200 and body.get("ok") else 1)

    if cmd == "capture":
        note = " ".join(sys.argv[2:]).strip()
        rid = str(uuid.uuid4())
        code, body = client.capture(
            rid,
            reason="look_at_this",
            context={"note": note} if note else {}
        )
        out({"http":code, **body})
        raise SystemExit(0 if code == 200 and body.get("ok") else 1)

    raise SystemExit(f"unknown command: {cmd}")

if __name__ == "__main__":
    main()
