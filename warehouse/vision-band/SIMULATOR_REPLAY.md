# Vision Band — Simulator Replay v0.1

This replay proves the interface before the physical board exists.

## Test sequence

1. Start simulator.
2. GET /status -> must report parked.
3. POST /capture while parked -> must FAIL with parked_mode.
4. POST /mode {"mode":"active"} -> must pass.
5. POST /capture -> must pass and return capture_id.
6. GET returned image_path -> must return payload.
7. GET /status -> must show last_capture_ms.
8. POST /mode {"mode":"parked"}.
9. POST /capture -> must fail again.

## Pass condition
The phone/bridge can be built against this contract now.
When the XIAO hardware arrives, only the endpoint implementation changes; the upstream workflow does not.
