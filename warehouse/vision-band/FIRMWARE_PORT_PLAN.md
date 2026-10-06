# Vision Band — Firmware Port Plan v0.1

Status: READY FOR HARDWARE
Target: Seeed XIAO ESP32-S3 Sense

## Goal
Implement the already-tested Vision Band endpoint contract on the real board without changing upstream Three Amigos behavior.

## Donor source
Use official Seeed XIAO ESP32-S3 Sense camera examples for board/camera initialization and OpenGlass/OpenSQZ patterns for wearable HTTP camera serving.

Do NOT copy an entire donor stack blindly.
FRANK only these functions:
- camera_init
- capture_jpeg
- wifi_connect
- http_serve
- status_report
- active_indicator
- power/battery_report where available

## Required contract
Real firmware must provide:
- GET /status
- POST /ping
- POST /mode
- POST /capture
- GET /captures/<id>.jpg

The JSON shape must stay compatible with ENDPOINT_PROTOCOL.md.

## State machine

BOOT
-> CONNECTING
-> PARKED

PARKED
- capture refused
- active LED off
- POST /mode active -> ACTIVE

ACTIVE
- still image capture allowed
- indicator ON during actual capture
- POST /mode parked -> PARKED

DEGRADED
- connection/camera fault explicitly reported
- no fake successful captures

## Version 1 choices
- still images only
- one camera only
- no continuous streaming required
- local Wi-Fi HTTP
- no cloud credentials on wearable
- no GPS on wearable
- no display
- phone supplies context

## Security / privacy
- prototype operates on trusted local network only
- camera capture disabled in PARKED
- indicator required for every capture
- no hidden background continuous recording
- do not store external service API keys on board

## Hardware arrival sequence
1. Flash known-good official camera example.
2. Confirm serial boot + camera initialization.
3. Capture one local JPEG.
4. Confirm Wi-Fi connection.
5. Add /ping and /status.
6. Add parked/active state machine.
7. Add /capture.
8. Run the exact simulator replay against real hardware.
9. Only after GREEN: battery, band, smoked window, outdoor tests.

## Replacement rule
If XIAO hardware proves unsuitable, replace only the endpoint implementation. Upstream client/Three Amigos remains unchanged.
