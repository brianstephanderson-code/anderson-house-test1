# Vision Band — Prototype Specification v0.1

Status: TRANSFORM READY
Project: Anderson House / Three Amigos
Purpose: A low-cost, removable wearable vision endpoint that can mount to many hats/headgear and hand visual context to the phone/Three Amigos.

## Locked design decisions

- Function first, device last.
- The band is the reusable function; the hat is only a shell.
- Velcro/hook-and-loop style mounting rather than buckle-heavy straps.
- Minimal smoked optical window: only large enough for the camera's usable field of view.
- Rear position = parked/socially legible non-use position.
- Turn hat around = deliberate active vision position.
- Visible status indicator when camera is active.
- Phone remains the bridge; Three Amigos remains the upstream brain/state.
- No new recurring paid service required.
- New hardware/function must pass REPLAY realistic work before production use.

## Donor architecture

Prefer proven/open patterns rather than custom electronics from scratch:

- XIAO ESP32-S3 Sense class board for compact camera + Wi-Fi/Bluetooth.
- OpenGlass/OpenSQZ style thin-wearable / upstream-compute split.
- ESP32-to-Android image handoff patterns.
- Visionbridge-style transport/battery/status patterns.

## Version 1 hardware target

- 1 camera only (wide angle). Do not add stereo/side cameras until a real need appears.
- XIAO ESP32-S3 Sense class board or equivalent.
- Small LiPo battery.
- Hook-and-loop adjustable band.
- Small smoked optical window/shroud.
- Visible activity LED.
- Simple power switch.
- Phone connectivity by Wi-Fi/BLE.
- Optional microphone only if headset/phone mic is insufficient.

## Physical layout

- Camera module centered or slightly off-center in band according to fit.
- Optical window should be as small as practical while avoiding vignetting.
- Battery located away from lens for balance.
- Electronics distributed along band where practical.
- Band must detach from hat quickly and move to another hat.
- No sharp edges or rigid protrusions toward the wearer.

## Operating modes

### Parked mode
- Hat worn normally.
- Vision Band sits at rear.
- Camera not intended for active capture.
- Camera disabled by default where feasible.

### Active mode
- User deliberately rotates hat so band is forward-facing.
- Camera may be activated by voice or explicit control.
- Visible activity indicator on while capture is active.

## Endpoint contract

The wearable should expose only what the upstream system needs:

- SEE: provide image/frame/video snapshot.
- REPORT: battery, connectivity, error/status.
- CONNECT: maintain link to phone bridge.
- PRIVACY: visible active indicator; optional physical shutter in later version.

All reasoning, long-term state, search, memory, verification, and routing remain upstream.

## First replay suite

Before GREEN:

1. Put band on cap; move it to a second cap.
2. Parked mode: confirm no intended forward capture.
3. Rotate hat to active mode; verify usable forward framing.
4. Voice request: “look at this” -> obtain one image -> send upstream -> receive result.
5. Walk outdoors; check motion and framing.
6. Bright sun test.
7. Indoor low-light test.
8. Battery runtime test.
9. Wi-Fi/BLE reconnect after temporary loss.
10. Reboot phone and reconnect.
11. Confirm indicator is clearly visible while camera active.
12. Confirm optical window does not visibly degrade image beyond acceptable level.

## GREEN gate

Prototype becomes GREEN only when:
- forward framing is consistently useful in active orientation,
- the band can move between hats without rewiring,
- phone bridge reconnects reliably,
- image quality is good enough for Three Amigos vision tasks,
- activity state is socially obvious,
- no recurring paid service is required,
- replay suite passes.

## Cost target

Initial prototype target: approximately US$30–$50 using commodity/open hardware and an existing phone/headset.

## Current status

CAST: CLOSED
RECAST: CLOSED
DONOR ARCHITECTURE: FOUND
FRANK DESIGN: GREEN
TRANSFORM: READY
PHYSICAL ASSEMBLY: requires parts and human hands
