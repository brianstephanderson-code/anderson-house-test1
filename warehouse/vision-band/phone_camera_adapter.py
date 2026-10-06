#!/usr/bin/env python3
"""Phone-camera substitute for the Vision Band endpoint contract.

Runs in Termux on Android. Uses termux-camera-photo when available.
This lets the phone act as the "real eye" before the wearable hardware arrives.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json, os, subprocess, time, uuid

HOST = os.environ.get("VISION_PHONE_HOST", "0.0.0.0")
PORT = int(os.environ.get("VISION_PHONE_PORT", "8787"))
CAMERA_ID = os.environ.get("VISION_PHONE_CAMERA_ID", "0")
ROOT = Path.home() / "anderson-house-mailbox" / "tomo_bridge" / "vision_phone_camera"
CAPTURES = ROOT / "captures"
CAPTURES.mkdir(parents=True, exist_ok=True)

STATE = {
    "mode": "parked",
    "last_capture_ms": None,
    "indicator": False,
    "camera": "unknown",
}

def send_json(h, code, obj):
    raw = json.dumps(obj).encode("utf-8")
    h.send_response(code)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(raw)))
    h.end_headers()
    h.wfile.write(raw)

def camera_available():
    from shutil import which
    return which("termux-camera-photo") is not None

def capture_photo(path):
    cmd = ["termux-camera-photo", "-c", str(CAMERA_ID), str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "camera command failed").strip())
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError("camera returned no image")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _body(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        if self.path == "/status":
            STATE["camera"] = "ready" if camera_available() else "error"
            return send_json(self, 200, {
                "device": "vision-phone-camera-v1",
                "state": STATE["mode"],
                "camera": STATE["camera"],
                "battery_percent": None,
                "rssi": None,
                "active_indicator": STATE["indicator"],
                "last_capture_ms": STATE["last_capture_ms"],
            })

        if self.path.startswith("/captures/"):
            name = self.path.split("/")[-1]
            path = CAPTURES / name
            if not path.exists():
                return send_json(self, 404, {"ok": False, "error": "not_found"})
            raw = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            return self.wfile.write(raw)

        return send_json(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        body = self._body()

        if self.path == "/ping":
            return send_json(self, 200, {
                "ok": True,
                "device": "vision-phone-camera-v1",
                "camera_available": camera_available(),
            })

        if self.path == "/mode":
            mode = body.get("mode")
            if mode not in ("parked", "active"):
                return send_json(self, 400, {"ok": False, "error": "bad_mode"})
            STATE["mode"] = mode
            return send_json(self, 200, {"ok": True, "mode": mode})

        if self.path == "/capture":
            if STATE["mode"] != "active":
                return send_json(self, 409, {"ok": False, "error": "parked_mode"})
            if not camera_available():
                return send_json(self, 503, {"ok": False, "error": "phone_camera_unavailable"})

            capture_id = str(uuid.uuid4())
            path = CAPTURES / f"{capture_id}.jpg"
            STATE["indicator"] = True
            try:
                capture_photo(path)
                now = int(time.time() * 1000)
                STATE["last_capture_ms"] = now
                return send_json(self, 200, {
                    "request_id": body.get("request_id"),
                    "ok": True,
                    "capture_id": capture_id,
                    "mime": "image/jpeg",
                    "image_path": f"/captures/{capture_id}.jpg",
                    "captured_at_ms": now,
                    "width": None,
                    "height": None,
                    "source": "android_phone_camera",
                })
            except Exception as exc:
                return send_json(self, 500, {"ok": False, "error": "camera_error", "detail": str(exc)})
            finally:
                STATE["indicator"] = False

        return send_json(self, 404, {"ok": False, "error": "not_found"})

if __name__ == "__main__":
    print(f"Vision Phone Camera adapter on http://{HOST}:{PORT}")
    print("camera available:", camera_available())
    HTTPServer((HOST, PORT), Handler).serve_forever()
