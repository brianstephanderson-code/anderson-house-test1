# Vision Band — Pre-Build REPLAY v0.1

Status: ACTIVE
Purpose: Test the design logic before spending money or assembling hardware.

## Rule

No physical build proceeds to production until the function survives representative REPLAY and then real-world validation.

## Stage A — Paper/Simulation REPLAY

Run each scenario against the current design:

1. **Job-to-job driving**
   - User wears band parked at rear.
   - Uses Bluetooth mic/earpiece, GPS, maps, job state.
   - Camera remains inactive unless deliberately requested.
   - PASS if workflow can stay hands-free and eyes-forward.

2. **Arrive at job / inspect**
   - Rotate hat/band to active orientation.
   - Ask: “Look at this.”
   - Capture one image and associate it with current job/location/time.
   - PASS if the function chain is unambiguous.

3. **Field diagnosis**
   - User looks at wiring/equipment and asks a question.
   - System must separate observation from inference and retrieve supporting docs.
   - PASS if answer can cite source and avoid pretending certainty.

4. **Document completed work**
   - User says: “Save this as completed.”
   - Capture image + voice note + job context.
   - PASS if stored as a structured record without extra phone handling.

5. **Move band to another hat**
   - Detach band, attach to second hat.
   - No rewiring or reconfiguration.
   - PASS if function is preserved independently of hat.

6. **Privacy / parked mode**
   - Band at rear / camera disabled by default.
   - Active capture requires deliberate activation.
   - Visible indicator required during capture.
   - PASS if bystander-facing use is legible.

7. **Connectivity loss**
   - Phone link drops and returns.
   - Endpoint reports degraded state and reconnects.
   - PASS if no silent false-success state occurs.

8. **Low light / bright sun**
   - Evaluate expected camera limits before hardware choice.
   - PASS if chosen donor camera can meet minimum useful-image threshold.

9. **Battery / heat / comfort**
   - Estimate expected runtime and component heat from donor hardware.
   - PASS if proposed placement is plausible for head-worn use.

10. **No-cloud / partial-service mode**
    - Internet unavailable.
    - Local capture and deferred upload still work where practical.
    - PASS if failure mode is graceful and clear.

## Stage B — Donor Verification

Before purchase:
- verify current donor hardware specs,
- verify camera field of view,
- verify battery/charging method,
- verify Android handoff method,
- verify open-source license,
- verify no paid recurring service is required.

## Stage C — Physical Frank

After Stage A/B GREEN:
- buy/assemble one-camera prototype,
- mount in hook-and-loop band,
- add tiny smoked window,
- add active indicator,
- connect to Android bridge.

## Stage D — Real-World REPLAY

Repeat the same scenarios with the actual prototype and record:
- PASS / FAIL,
- latency,
- reconnect behavior,
- framing,
- image quality,
- comfort,
- runtime,
- social/privacy legibility.

## Current gate

PRE-BUILD REPLAY: STARTED
PHYSICAL BUILD: HELD
PURCHASE: HELD
PRODUCTION GREEN: NOT YET
