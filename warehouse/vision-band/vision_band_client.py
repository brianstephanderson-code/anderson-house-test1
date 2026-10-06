#!/usr/bin/env python3
"""Tiny client for the Vision Band endpoint contract.

Standard-library only so it can run in Termux, Android-adjacent Python,
CI, or a normal host without new subscriptions or dependencies.
"""
import json
from urllib import request, error

class VisionBandError(RuntimeError):
    pass

class VisionBandClient:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _json(self, method, path, payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(
            self.base_url + path,
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw.decode("utf-8"))
        except error.HTTPError as exc:
            raw = exc.read()
            try:
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {"ok": False, "error": f"http_{exc.code}"}
            return exc.code, body
        except Exception as exc:
            raise VisionBandError(f"link_error: {exc}") from exc

    def ping(self):
        return self._json("POST", "/ping", {})

    def status(self):
        return self._json("GET", "/status")

    def set_mode(self, mode):
        if mode not in ("parked", "active"):
            raise ValueError("mode must be parked or active")
        return self._json("POST", "/mode", {"mode": mode})

    def capture(self, request_id, reason="look_at_this", context=None):
        payload = {
            "request_id": request_id,
            "reason": reason,
            "context": context or {},
        }
        return self._json("POST", "/capture", payload)

    def fetch_capture(self, image_path):
        req = request.Request(self.base_url + image_path, method="GET")
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status, resp.headers.get("Content-Type"), resp.read()
        except Exception as exc:
            raise VisionBandError(f"capture_fetch_error: {exc}") from exc
