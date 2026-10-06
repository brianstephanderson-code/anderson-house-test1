#!/usr/bin/env python3
"""Privacy-safe local Vision endpoint helpers for Termux bridge v2."""
import hashlib
import json
from pathlib import Path
from urllib import request, error

BASE = "http://127.0.0.1:8787"
PRIVATE_ROOT = Path.home() / ".tomo_private_vision"

def _http(method, path, payload=None, timeout=20):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(BASE + path, data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get_content_type(), r.read()
    except error.HTTPError as e:
        return e.code, e.headers.get_content_type(), e.read()

def _json(method, path, payload=None, timeout=20):
    code, ctype, raw = _http(method, path, payload, timeout)
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        data = {"raw": raw[:500].decode("utf-8", "replace")}
    return code, data

def vision_status():
    code, data = _json("GET", "/status")
    return {"ok": code == 200, "http": code, "status": data}

def vision_mode(mode):
    if mode not in {"active", "parked"}:
        raise ValueError("mode must be active or parked")
    code, data = _json("POST", "/mode", {"mode": mode})
    return {"ok": code == 200 and bool(data.get("ok")), "http": code, "mode": data}

def vision_capture(request_id, note=""):
    request_id = str(request_id or "").strip()
    if not request_id or len(request_id) > 128:
        raise ValueError("request_id must be 1-128 characters")
    note = str(note or "").strip()
    if len(note) > 500:
        raise ValueError("note too long")

    code, data = _json(
        "POST",
        "/capture",
        {
            "request_id": request_id,
            "reason": "look_at_this",
            "context": {"note": note} if note else {},
        },
        timeout=30,
    )
    if code != 200 or not data.get("ok"):
        return {"ok": False, "http": code, "capture": data}

    image_path = data.get("image_path")
    if not isinstance(image_path, str) or not image_path.startswith("/captures/"):
        return {"ok": False, "http": code, "capture": data, "error": "missing_image_path"}

    img_code, ctype, raw = _http("GET", image_path, timeout=30)
    if img_code != 200 or ctype != "image/jpeg" or len(raw) < 1000:
        return {
            "ok": False,
            "http": code,
            "capture": data,
            "fetch_http": img_code,
            "content_type": ctype,
            "bytes": len(raw),
            "error": "invalid_jpeg_return",
        }

    PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        PRIVATE_ROOT.chmod(0o700)
    except OSError:
        pass

    capture_id = str(data.get("capture_id") or request_id)
    safe = "".join(ch for ch in capture_id if ch.isalnum() or ch in "._-")[:128] or "capture"
    local_path = PRIVATE_ROOT / f"{safe}.jpg"
    local_path.write_bytes(raw)
    try:
        local_path.chmod(0o600)
    except OSError:
        pass

    # Important: never put image bytes or the private absolute path in the public GitHub result.
    return {
        "ok": True,
        "http": code,
        "capture_id": data.get("capture_id"),
        "request_id": data.get("request_id"),
        "mime": data.get("mime"),
        "width": data.get("width"),
        "height": data.get("height"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "private_local_saved": True,
    }
