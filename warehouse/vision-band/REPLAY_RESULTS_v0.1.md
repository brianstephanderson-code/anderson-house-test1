# Vision Band — Pre-Build REPLAY Results v0.1

Date: 2026-10-06
Status: PRE-BUILD REPLAY COMPLETE — CONDITIONAL GREEN

## Summary

The current one-camera removable Vision Band concept survives the paper/simulation replay well enough to proceed to donor-hardware selection and then a physical prototype.

The main result is that the core architecture does not require new invention:
- ESP32-S3 class wearable camera hardware already exists.
- Camera + microphone on wearable / heavier inference upstream is already demonstrated in OpenGlass-style projects.
- Wi-Fi transport from wearable to a nearby host is already demonstrated.
- Small LiPo battery operation is already demonstrated in donor projects.
- The XIAO ESP32-S3 Sense is physically small enough for a band prototype and supports Wi-Fi, BLE, camera, microphone, and battery power.

## Replay Results

### 1. Job-to-job driving
Result: GREEN WITH SAFETY GATE
- Camera can remain inactive/parked at rear.
- Voice, GPS, map, job state, and audio output do not depend on active camera.
- The wearable adds optional context without becoming the primary driving interface.
- Hard rule: no screen-heavy interaction or attention-diverting prompts while moving.

### 2. Arrive at job / inspect
Result: GREEN
- Rotate hat/band to forward active position.
- Deliberate image capture is technically consistent with donor hardware.
- Context can be associated upstream with job/location/time.

### 3. Field diagnosis
Result: GREEN WITH VERIFICATION GATE
- Live image -> upstream vision/doc retrieval is feasible.
- System must distinguish OBSERVATION from INFERENCE.
- Safety-critical answers must cite source/manual/standard where available and leave final engineering judgement to the qualified user.

### 4. Document completed work
Result: GREEN
- Capture image + voice note + current job context is straightforward at architecture level.
- No need for heavy compute on the band.

### 5. Move band to another hat
Result: GREEN BY DESIGN
- Function is independent of hat if electronics remain on removable hook-and-loop band.
- No software reconfiguration should be needed after physical relocation.

### 6. Privacy / parked mode
Result: GREEN WITH REQUIRED CONTROL
- Rear position is a useful social/physical parked state.
- Camera should be disabled by default in parked mode where practical.
- Active capture must have a visible indicator.
- Future optional physical shutter remains desirable but is not required for prototype v1.

### 7. Connectivity loss
Result: AMBER -> ACCEPTABLE FOR PROTOTYPE
- Donor systems use Wi-Fi and obtain device IP by DHCP; addresses can change after restart.
- Prototype must detect disconnect and report degraded state rather than silently claiming success.
- Reconnect logic is a required physical-replay test.

### 8. Bright sun / low light
Result: AMBER -> PHYSICAL TEST REQUIRED
- Camera hardware supports useful resolutions, but actual smoked-window transmission, glare, motion, and low-light performance cannot be closed on paper.
- The smoked window must stay extremely small and close to the lens, and should be tested with clear/tinted alternatives.

### 9. Battery / heat / comfort
Result: AMBER -> PHYSICAL TEST REQUIRED
- Official XIAO ESP32-S3 Sense figures show compact dimensions around 21 x 17.8 x 15 mm with Sense expansion.
- Active Wi-Fi/camera use draws materially more power than sleep/idle.
- 250 mAh-class donor batteries are already used in OpenGlass-style builds, but actual runtime and skin-adjacent heat must be measured.
- Battery should be placed away from the camera module for balance and away from pressure points.

### 10. No-cloud / partial-service mode
Result: GREEN FOR CAPTURE, AMBER FOR INFERENCE
- Local capture and local-network transfer can exist independently of cloud AI.
- Full reasoning depends on whatever upstream model/service is available.
- Desired fallback: save image + context locally and defer processing.

## Donor Verification

### Seeed XIAO ESP32-S3 Sense
Verified:
- ESP32-S3 dual-core up to 240 MHz.
- 2.4 GHz Wi-Fi.
- BLE 5.0 / Bluetooth Mesh.
- Integrated camera expansion and digital microphone.
- 8 MB PSRAM + 8 MB flash.
- Approximate Sense dimensions: 21 x 17.8 x 15 mm with expansion.
- 3.7 V battery input and battery-power support.
- Current production Sense documentation references OV3660 camera; older donor projects may reference OV2640.
- Camera and microphone examples are officially documented.

### OpenGlass / OpenSQZ pattern
Verified:
- ESP32-S3 wearable side captures camera and microphone.
- Nearby host performs heavier inference and response work.
- Camera capture over HTTP and audio over WebSocket are demonstrated.
- Session replay/evaluation tooling exists in OpenSQZ/OpenGlass.

### OpenGlass donor build
Verified:
- Public donor builds use XIAO ESP32-S3 Sense plus a small 3.7 V 250 mAh LiPo.
- MIT-licensed versions exist.
- Older OpenGlass repos may be archived/moved; use as donor patterns rather than blindly adopting whole stack.

### Visionbridge
Verified:
- ESP32 wearable firmware patterns exist for camera capture, WebSocket/MQTT transport, battery reporting, wake/audio handling, MCP-style device controls.
- MIT licensed.

## Design Changes From Replay

1. Keep v1 to ONE camera.
2. Make reconnect/degraded-state reporting mandatory.
3. Make active LED mandatory.
4. Do not finalize smoked-window material before A/B optical testing.
5. Add local deferred-capture fallback.
6. Do not claim runtime until measured.
7. Do not assume old OV2640 donor BOM matches current XIAO Sense production hardware; verify current camera variant at purchase time.
8. Keep all heavy reasoning upstream.

## Gate Decision

CAST: CLOSED
RECAST: CLOSED
PAPER REPLAY: PASS
DONOR VERIFICATION: PASS WITH HARDWARE-VARIANT NOTE
DESIGN: CONDITIONAL GREEN
PURCHASE: MAY PROCEED AFTER CURRENT-PARTS/BOM CHECK
PHYSICAL BUILD: NEXT STAGE
REAL-WORLD REPLAY: REQUIRED BEFORE PRODUCTION GREEN

## Next Action

Prepare a current, lowest-cost BOM using currently available components and verify:
- exact XIAO Sense camera variant,
- battery compatibility and charging,
- optical-window candidate,
- band material,
- simple enclosure/shroud,
- visible indicator,
- connector/mounting method.

Do not purchase until BOM is checked against current availability and total cost target.
