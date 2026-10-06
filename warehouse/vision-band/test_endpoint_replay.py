#!/usr/bin/env python3
"""Automated replay of the Vision Band endpoint contract."""
import pathlib
import subprocess
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from vision_band_client import VisionBandClient

sim = subprocess.Popen(
    [sys.executable, str(HERE / "simulate_vision_band.py")],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

client = VisionBandClient("http://127.0.0.1:8787", timeout=2)

try:
    for _ in range(30):
        try:
            code, body = client.ping()
            if code == 200 and body.get("ok"):
                break
        except Exception:
            pass
        time.sleep(0.1)
    else:
        raise AssertionError("simulator did not become ready")

    code, st = client.status()
    assert code == 200
    assert st["state"] == "parked"

    code, body = client.capture(str(uuid.uuid4()))
    assert code == 409
    assert body["error"] == "parked_mode"

    code, body = client.set_mode("active")
    assert code == 200 and body["ok"] is True

    rid = str(uuid.uuid4())
    code, cap = client.capture(rid, context={"job_id": "replay-job-1"})
    assert code == 200
    assert cap["ok"] is True
    assert cap["request_id"] == rid
    assert cap["capture_id"]

    code, mime, payload = client.fetch_capture(cap["image_path"])
    assert code == 200
    assert payload == b"VISION_BAND_SIMULATED_CAPTURE"

    code, st = client.status()
    assert code == 200
    assert st["last_capture_ms"] is not None

    code, body = client.set_mode("parked")
    assert code == 200 and body["mode"] == "parked"

    code, body = client.capture(str(uuid.uuid4()))
    assert code == 409
    assert body["error"] == "parked_mode"

    print("VISION_BAND_ENDPOINT_REPLAY_GREEN")
finally:
    sim.terminate()
    try:
        sim.wait(timeout=2)
    except subprocess.TimeoutExpired:
        sim.kill()
