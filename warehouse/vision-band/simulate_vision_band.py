#!/usr/bin/env python3
"""Vision Band endpoint simulator.

Purpose:
Replay the phone/Three-Amigos integration contract before physical hardware exists.
No camera required. It serves a generated placeholder JPEG-like test payload only when
mode is ACTIVE, so the Android/bridge side can be developed independently.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json, time, uuid

STATE = {
    "mode": "parked",
    "last_capture_ms": None,
    "battery_percent": 100,
    "indicator": False,
}

def send_json(h, code, obj):
    raw = json.dumps(obj).encode()
    h.send_response(code)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(raw)))
    h.end_headers()
    h.wfile.write(raw)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _body(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode())
        except Exception:
            return {}

    def do_GET(self):
        if self.path == "/status":
            return send_json(self, 200, {
                "device": "vision-band-v1-sim",
                "state": STATE["mode"],
                "camera": "ready",
                "battery_percent": STATE["battery_percent"],
                "rssi": None,
                "active_indicator": STATE["indicator"],
                "last_capture_ms": STATE["last_capture_ms"],
            })
        if self.path.startswith("/captures/"):
            # Minimal deterministic payload for transport testing.
            # Hardware version will return a real JPEG.
            payload = b"VISION_BAND_SIMULATED_CAPTURE"
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            return self.wfile.write(payload)
        return send_json(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        body = self._body()
        if self.path == "/ping":
            return send_json(self, 200, {"ok": True, "device": "vision-band-v1-sim"})

        if self.path == "/mode":
            mode = body.get("mode")
            if mode not in ("parked", "active"):
                return send_json(self, 400, {"ok": False, "error": "bad_mode"})
            STATE["mode"] = mode
            return send_json(self, 200, {"ok": True, "mode": mode})

        if self.path == "/capture":
            if STATE["mode"] != "active":
                return send_json(self, 409, {"ok": False, "error": "parked_mode"})

            STATE["indicator"] = True
            capture_id = str(uuid.uuid4())
            now = int(time.time() * 1000)
            STATE["last_capture_ms"] = now
            # Simulate a short capture while preserving the visible-indicator rule.
            time.sleep(0.05)
            STATE["indicator"] = False

            return send_json(self, 200, {
                "request_id": body.get("request_id"),
                "ok": True,
                "capture_id": capture_id,
                "mime": "image/jpeg",
                "image_path": f"/captures/{capture_id}.jpg",
                "captured_at_ms": now,
                "width": 0,
                "height": 0,
                "simulated": True,
            })

        return send_json(self, 404, {"ok": False, "error": "not_found"})

if __name__ == "__main__":
    print("Vision Band simulator on http://0.0.0.0:8787")
    HTTPServer(("0.0.0.0", 8787), Handler).serve_forever()
