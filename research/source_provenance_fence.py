#!/usr/bin/env python3
"""Small fail-closed provenance fence for fetched research evidence.

This function does not decide whether a claim is true. It only checks that
an evidence item carries enough provenance to be independently verified later.
"""

REQUIRED_FIELDS = ("url", "fetched_at", "source_type", "evidence_lane", "content_sha256")
ALLOWED_LANES = frozenset({"official", "end_user", "independent", "other"})
ALLOWED_SOURCE_TYPES = frozenset({"primary", "official", "operator", "community", "independent", "other"})


def provenance_decision(item):
    """Return PASS only when required provenance is explicit and well-shaped."""
    reasons = []

    for field in REQUIRED_FIELDS:
        value = item.get(field)
        if not isinstance(value, str) or not value.strip():
            reasons.append("missing_or_invalid:" + field)

    url = item.get("url")
    if isinstance(url, str) and url.strip() and not url.startswith(("https://", "http://")):
        reasons.append("invalid_url_scheme")

    lane = item.get("evidence_lane")
    if isinstance(lane, str) and lane.strip() and lane not in ALLOWED_LANES:
        reasons.append("unknown_evidence_lane")

    source_type = item.get("source_type")
    if isinstance(source_type, str) and source_type.strip() and source_type not in ALLOWED_SOURCE_TYPES:
        reasons.append("unknown_source_type")

    digest = item.get("content_sha256")
    if isinstance(digest, str) and digest.strip():
        if len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            reasons.append("invalid_content_sha256")

    return {"decision": "PASS" if not reasons else "QUARANTINE", "reasons": reasons}


if __name__ == "__main__":
    good = {
        "url": "https://example.org/source",
        "fetched_at": "2026-10-01T21:40:00Z",
        "source_type": "official",
        "evidence_lane": "official",
        "content_sha256": "a" * 64,
    }
    assert provenance_decision(good)["decision"] == "PASS"

    for field in REQUIRED_FIELDS:
        bad = dict(good)
        bad.pop(field)
        assert provenance_decision(bad)["decision"] == "QUARANTINE", field

    bad_hash = dict(good)
    bad_hash["content_sha256"] = "not-a-hash"
    assert provenance_decision(bad_hash)["decision"] == "QUARANTINE"

    bad_lane = dict(good)
    bad_lane["evidence_lane"] = "mystery"
    assert provenance_decision(bad_lane)["decision"] == "QUARANTINE"

    bad_url = dict(good)
    bad_url["url"] = "file:///tmp/source"
    assert provenance_decision(bad_url)["decision"] == "QUARANTINE"

    print("PASS source_provenance_fence")
