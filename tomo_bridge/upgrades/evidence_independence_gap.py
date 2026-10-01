#!/usr/bin/env python3
"""Diagnose fake cross-checks where evidence is not actually independent.

Small reasoning function only. It does not search, fetch, rank, or decide truth.
"""
from urllib.parse import urlparse


def _norm(value):
    return " ".join(str(value or "").lower().split())


def _host(claim):
    host = _norm(claim.get("source_host"))
    if host:
        return host.removeprefix("www.")
    try:
        return (urlparse(str(claim.get("source_url") or "")).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


def diagnose_independence_gap(key, claims, minimum_independent_sources=2):
    """Require N distinct source families for verified evidence about one key.

    source_family may explicitly group mirrors/syndicated pages. Otherwise host is
    used as the conservative family identifier. Unknown provenance never counts
    as an independent source.
    """
    key = _norm(key)
    families = set()
    matched = 0
    for claim in claims or []:
        if _norm(claim.get("key")) != key or claim.get("verified") is not True:
            continue
        matched += 1
        family = _norm(claim.get("source_family")) or _host(claim)
        if family:
            families.add(family)

    need = max(1, int(minimum_independent_sources or 1))
    if len(families) >= need:
        return None
    return {
        "key": key,
        "reason": "insufficient_source_independence",
        "verified_claims": matched,
        "independent_sources": len(families),
        "required_independent_sources": need,
        "missing_count": need - len(families),
        "missing_lanes": ["independent"],
        "recast_hint": f"{key} independent corroboration different source",
    }


if __name__ == "__main__":
    duplicate = [
        {"key":"best bait", "verified":True, "source_url":"https://example.org/a"},
        {"key":"best bait", "verified":True, "source_url":"https://www.example.org/b"},
    ]
    gap = diagnose_independence_gap("best bait", duplicate)
    assert gap and gap["independent_sources"] == 1 and gap["missing_count"] == 1

    diverse = duplicate + [
        {"key":"best bait", "verified":True, "source_url":"https://users.example.net/report"}
    ]
    assert diagnose_independence_gap("best bait", diverse) is None

    mirrors = [
        {"key":"rule", "verified":True, "source_host":"agency.gov", "source_family":"agency"},
        {"key":"rule", "verified":True, "source_host":"mirror.example", "source_family":"agency"},
    ]
    assert diagnose_independence_gap("rule", mirrors)["independent_sources"] == 1

    unknown = [{"key":"rule", "verified":True}]
    assert diagnose_independence_gap("rule", unknown)["independent_sources"] == 0
    print("evidence_independence_gap: PASS")
