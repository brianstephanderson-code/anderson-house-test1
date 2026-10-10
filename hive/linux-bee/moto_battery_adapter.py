"""Convert a Termux:API battery status reading into a Linux Bee envelope."""
from datetime import datetime, timezone
import json
import math
import sys
from linux_bee import process

def convert(battery, device_id="moto_1", timestamp=None):
    if not isinstance(battery, dict):
        raise ValueError("battery reading must be an object")
    value = battery.get("temperature")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("missing or invalid battery temperature")
    # Termux:API battery status reports degrees Celsius.
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    return process({"device_id":device_id,"sensor_type":"temperature","timestamp":timestamp,
                    "payload":{"celsius":value,"source":"android_battery","measurement":"battery_not_room"}})

if __name__ == "__main__":
    try:
        print(json.dumps(convert(json.load(sys.stdin)), sort_keys=True))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status":"REJECTED","reason":str(exc)}))
        sys.exit(1)
