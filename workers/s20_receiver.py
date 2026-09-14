#!/usr/bin/env python3
import json, time, urllib.request
from pathlib import Path

REPO = "brianstephanderson-code/anderson-house-test1"
API = f"https://api.github.com/repos/{REPO}/contents/parcels"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/parcels"
HOME = Path.home() / "anderson-house-new"
INBOX = HOME / "inbox"
RECEIPTS = HOME / "receipts"
SEEN = HOME / ".s20-seen.json"
INTERVAL = 60

INBOX.mkdir(parents=True, exist_ok=True)
RECEIPTS.mkdir(parents=True, exist_ok=True)

try:
    seen = set(json.loads(SEEN.read_text()))
except Exception:
    seen = set()

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Anderson-House-S20"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")

print("S20 postman awake. Watching GitHub for parcels...")

while True:
    try:
        listing = json.loads(get(API))
        for item in listing:
            name = item.get("name", "")
            if not name.endswith(".md") or name in seen:
                continue

            text = get(f"{RAW}/{name}")
            if "TO: S20 / Worker" not in text:
                seen.add(name)
                continue

            # Aikido pre-check
            if "Parcel ID:" not in text or "## TRANSFORM" not in text:
                print(f"QUARANTINE: {name} failed pre-check")
                continue

            (INBOX / name).write_text(text)

            parcel_id = "UNKNOWN"
            for line in text.splitlines():
                if line.startswith("Parcel ID:"):
                    parcel_id = line.split(":", 1)[1].strip()
                    break

            receipt = (
                f"Parcel ID: {parcel_id}\n"
                f"Worker: S20\n"
                f"RECEIVED: YES\n"
                f"DELIVERY VERIFIED\n"
            )
            (RECEIPTS / f"{parcel_id}-RECEIPT.txt").write_text(receipt)
            print(f"DELIVERED: {parcel_id} -> S20 inbox")
            seen.add(name)

        SEEN.write_text(json.dumps(sorted(seen)))
    except Exception as e:
        print(f"Postman retry: {e}")

    time.sleep(INTERVAL)
