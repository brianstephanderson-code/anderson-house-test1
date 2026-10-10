"""Linux Bee: pure-stdlib sensor envelope validator and router (staging only)."""
import json
from datetime import datetime, timezone

KINDS = {"audio", "temperature", "camera", "location"}

def process(message):
    if not isinstance(message, dict):
        raise ValueError("message must be an object")
    required = ("device_id", "sensor_type", "timestamp", "payload")
    if any(k not in message for k in required):
        raise ValueError("missing required field")
    device = message["device_id"]
    kind = message["sensor_type"]
    if not isinstance(device, str) or not (1 <= len(device) <= 64) or not all(c.isalnum() or c in "-_" for c in device):
        raise ValueError("invalid device_id")
    if kind not in KINDS:
        raise ValueError("unsupported sensor_type")
    timestamp = message["timestamp"]
    if not isinstance(timestamp, str):
        raise ValueError("invalid timestamp")
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    payload = message["payload"]
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    if len(json.dumps(payload)) > 4096:
        raise ValueError("payload too large")
    if kind == "temperature":
        value = payload.get("celsius")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not (-100 <= value <= 200):
            raise ValueError("invalid temperature")
    # Audio/camera messages carry metadata only, never raw recordings.
    if kind in {"audio", "camera"} and any(k in payload for k in ("raw", "base64", "bytes")):
        raise ValueError("raw media not accepted")
    return {"status": "ACCEPTED", "device_id": device, "route": "sensor/" + kind,
            "timestamp": dt.astimezone(timezone.utc).isoformat(), "payload": payload}

if __name__ == "__main__":
    import sys
    try:
        print(json.dumps(process(json.load(sys.stdin)), sort_keys=True))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}))
        sys.exit(1)
