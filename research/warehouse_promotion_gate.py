#!/usr/bin/env python3
"""Small fail-closed gate between verification/testing and warehouse promotion."""

REQUIRED_LANES = frozenset({"official", "end_user"})


def promotion_decision(record):
    """Return PROMOTE only when every required verification fact is explicit."""
    reasons = []

    if record.get("provenance_ok") is not True:
        reasons.append("provenance_not_verified")

    lanes = set(record.get("evidence_lanes") or [])
    missing = sorted(REQUIRED_LANES - lanes)
    if missing:
        reasons.append("missing_evidence_lanes:" + ",".join(missing))

    if record.get("verify_passed") is not True:
        reasons.append("verification_not_passed")

    if record.get("tests_run") is not True:
        reasons.append("tests_not_run")
    elif record.get("tests_passed") is not True:
        reasons.append("tests_not_passed")

    return {
        "decision": "PROMOTE" if not reasons else "QUARANTINE",
        "reasons": reasons,
    }


if __name__ == "__main__":
    good = {
        "provenance_ok": True,
        "evidence_lanes": ["official", "end_user"],
        "verify_passed": True,
        "tests_run": True,
        "tests_passed": True,
    }
    assert promotion_decision(good)["decision"] == "PROMOTE"

    for key in ("provenance_ok", "verify_passed", "tests_run", "tests_passed"):
        bad = dict(good)
        bad[key] = False
        assert promotion_decision(bad)["decision"] == "QUARANTINE", key

    missing_lane = dict(good)
    missing_lane["evidence_lanes"] = ["official"]
    assert promotion_decision(missing_lane)["decision"] == "QUARANTINE"

    unknown = dict(good)
    unknown.pop("tests_passed")
    assert promotion_decision(unknown)["decision"] == "QUARANTINE"

    print("PASS warehouse_promotion_gate")
