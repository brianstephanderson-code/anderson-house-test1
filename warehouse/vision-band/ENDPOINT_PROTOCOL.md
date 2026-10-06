# Vision Band — Endpoint Contract v0.1

Status: PRE-HARDWARE REPLAYABLE
Goal: make the wearable replaceable. Three Amigos talks to a simple contract, not to one specific board.

## Transport
Prototype v1: local Wi-Fi HTTP on the same trusted network/hotspot as the Android bridge.
BLE is reserved for discovery/control if needed later.

## Required endpoints

### GET /status
Returns JSON:
{
  "device": "vision-band-v1",
  "state": "parked|active|degraded",
  "camera": "ready|busy|error",
  "battery_percent": 0-100 or null,
  "rssi": integer or null,
  "active_indicator": true|false,
  "last_capture_ms": integer or null
}

### POST /mode
Request JSON:
{"mode":"parked"} or {"mode":"active"}

Rules:
- parked => camera capture disabled unless explicitly overridden by a local physical test command.
- active => capture allowed.
- active indicator must illuminate whenever an actual capture is underway.

### POST /capture
Request JSON:
{
  "request_id": "uuid/string",
  "reason": "look_at_this",
  "context": {
    "job_id": "optional",
    "location": "optional supplied by phone",
    "note": "optional"
  }
}

Response JSON:
{
  "request_id": "...",
  "ok": true,
  "capture_id": "...",
  "mime": "image/jpeg",
  "image_path": "/captures/<id>.jpg",
  "captured_at": "ISO-8601",
  "width": integer,
  "height": integer
}

### GET /captures/<id>.jpg
Returns JPEG bytes.

### POST /ping
Returns:
{"ok":true,"device":"vision-band-v1"}

## Failure behavior
Never fake success.
Use explicit errors such as:
- parked_mode
- camera_busy
- camera_error
- low_battery
- storage_full
- link_degraded

## Upstream rule
The band does not decide what an image means.
It only:
SEE -> REPORT -> CONNECT -> PRIVACY.

Phone/Three Amigos adds:
location, job, time, maps, memory, search, inference, verification, and speech.

## Privacy rule
Capture event = indicator ON.
Capture finished = indicator OFF unless continuous active mode is explicitly enabled.
Prototype defaults to still-image capture, not continuous recording.
