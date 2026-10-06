#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tomo_bridge"))
from vision_actions import vision_status, vision_mode, vision_capture

sim = subprocess.Popen(
    [sys.executable, str(ROOT / "warehouse/vision-band/simulate_vision_band.py")],
    cwd=ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
try:
    for _ in range(40):
        try:
            s = vision_status()
            if s.get("ok"):
                break
        except Exception:
            pass
        time.sleep(0.1)
    else:
        raise SystemExit("simulator did not start")

    s = vision_status()
    assert s["ok"] and s["status"]["state"] == "parked", s

    blocked = vision_capture("termux-v2-test-blocked")
    assert not blocked["ok"] and blocked["http"] == 409, blocked

    a = vision_mode("active")
    assert a["ok"], a

    cap = vision_capture("termux-v2-test-active", "CI privacy-safe replay")
    assert cap["ok"], cap
    assert cap["mime"] == "image/jpeg", cap
    assert cap["bytes"] > 0, cap
    assert cap["private_local_saved"] is True, cap
    assert "private_path" not in cap and "local_path" not in cap, cap

    p = vision_mode("parked")
    assert p["ok"], p

    blocked2 = vision_capture("termux-v2-test-reparked")
    assert not blocked2["ok"] and blocked2["http"] == 409, blocked2

    print("TERMUX_V2_VISION_ACTIONS_REPLAY_GREEN")
finally:
    sim.terminate()
    try:
        sim.wait(timeout=3)
    except subprocess.TimeoutExpired:
        sim.kill()
