# Vision Band — Current Prototype BOM v0.1

Date: 2026-10-06
Status: BOM CHECK COMPLETE — READY FOR FIRST PHYSICAL FRANK

## Core rule
Version 1 proves the function with the fewest parts possible. One camera only. No custom PCB. No display. No new subscription. Phone remains the bridge; Three Amigos remains upstream.

## Required parts

### 1) Camera / compute board — PRIMARY
**Seeed Studio XIAO ESP32-S3 Sense**
- Current official price checked: about US$13.90–$13.99.
- In stock at Seeed at time of check.
- Integrated camera + digital microphone.
- 2.4 GHz Wi-Fi + BLE.
- 8 MB PSRAM + 8 MB flash + microSD slot.
- Built-in battery management / USB charging support.

Why this one:
- Small enough for head-worn prototype.
- Already matches the donor architecture.
- Avoids adding a separate camera board and microphone.

NOTE: Current Seeed product pages still reference OV2640 on the standard Sense listing, while Seeed also sells a higher-resolution OV5640 accessory camera separately. Do not assume the accessory camera is required for v1.

### 2) Battery
**Protected rechargeable 3.7 V LiPo, ~250 mAh initially**
- Target physical size roughly 20–30 mm long, ~5–6 mm thick.
- Current market examples are roughly US$2–$8 each depending on seller/connector.
- Seeed specifically recommends a qualified rechargeable 3.7 V lithium battery with protection.

Important:
- The bare XIAO ESP32-S3 Sense does not provide a convenient plug-in battery socket in the standard board form; Seeed documents soldering the battery to the battery pads.
- Therefore v1 either:
  A) solder a short removable lead/connector to the pads once, or
  B) use a tiny intermediary power lead.
- Do not repeatedly solder/desolder the LiPo itself.

### 3) Band
**20–25 mm soft hook-and-loop / Velcro-type strap**
- Prefer soft woven loop against skin/hat.
- Cut-to-length style is acceptable for prototype.
- Avoid heavy cargo/cinch straps; they are much thicker than needed.

Target:
- removable,
- washable once electronics are removed,
- no rigid buckle required,
- enough overlap to fit bare head or different hat shells.

### 4) Smoked optical window
**Tiny neutral smoked optical/plastic window**
Prototype approach:
- Start with a tiny clear window and a tiny light-smoke sample.
- Window should be only slightly larger than the usable lens aperture.
- Place as close to the lens as practical.
- A/B test clear vs smoke for:
  - daylight glare,
  - low light,
  - color shift,
  - vignetting,
  - focus.

Do NOT buy a large expensive sheet specifically for v1 if a small scrap/sample can be sourced.

### 5) Shroud / carrier
**Minimal black/dark flexible carrier**
First prototype options:
- heat-formable plastic,
- thin 3D-printed shell,
- cut/formed ABS/PETG,
- small fabric pocket with rigid lens insert.

Purpose only:
- hold board,
- hold lens/window alignment,
- keep electronics off skin,
- protect wiring.

### 6) Active indicator
**Small visible LED**
- Mandatory when active capture is occurring.
- Prefer front/side visibility.
- Software controlled where possible.
- Do not rely only on an internal charging LED.

### 7) Power control
**Tiny inline slide switch or physically accessible disconnect**
- Lets user positively disable the wearable.
- Prototype must have a clear OFF state.

## Optional / defer

Do NOT add these to v1 unless replay exposes a real need:
- second/third camera,
- GPS module,
- display,
- cellular modem,
- custom PCB,
- separate microphone,
- speaker,
- IMU,
- physical shutter (desirable later, but not required to prove the function).

The phone already supplies GPS, maps, cellular/data, large battery, UI and audio bridge.

## Cost envelope

Core electronics:
- XIAO ESP32-S3 Sense: ~US$14
- protected 250 mAh LiPo: ~US$3–$8
- strap material: ~US$3–$10 worth
- LED/switch/wire/connectors: a few dollars
- shroud/window: ideally scrap/sample/very low-cost material

Expected first Frank:
**roughly US$25–$40 before shipping**, still within the previous US$30–$50 target.

## Build order

1. Bench-test XIAO Sense over USB.
2. Prove one still image can reach the Android bridge.
3. Add battery and explicit power OFF.
4. Add active LED.
5. Mount board/battery temporarily on soft hook-and-loop band.
6. Test camera angle with NO smoked window.
7. Add clear micro-window.
8. A/B test smoked micro-window.
9. Fix final shroud only after optical/framing test.
10. Run the physical REPLAY suite.

## Purchase gate

GREEN TO BUY:
- one XIAO ESP32-S3 Sense,
- one or two protected 3.7 V ~250 mAh LiPo batteries,
- soft hook-and-loop strap material,
- tiny switch/LED/wire/connector,
- small clear + light-smoke optical samples.

HOLD:
- expensive enclosure,
- multiple cameras,
- custom board,
- production sewing,
- bulk parts.

## Current status

CAST: CLOSED
RECAST: CLOSED
PRE-BUILD REPLAY: PASS
DONOR HARDWARE: VERIFIED
BOM: CHECKED
COST GATE: PASS
FIRST PHYSICAL FRANK: READY
