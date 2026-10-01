#!/usr/bin/env python3
"""Diagnose stale/undated evidence without searching or deciding truth.

Small reasoning function for claims whose requirement explicitly needs current
evidence. It emits machine-readable gaps that gap_to_recast can consume later.
"""

from datetime import date, datetime


def _norm(value):
    return " ".join(str(value or "").lower().split())


def _year(value):
    if isinstance(value, (date, datetime)):
        return value.year
    text = str(value or "").strip()
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def diagnose_freshness(requirements, claims, current_year=None):
    """Return freshness gaps only for requirements marked current=True.

    A claim can carry effective_date, published_date, or year. Undated evidence
    is unknown rather than silently accepted. max_age_years defaults to 0, so a
    current requirement normally needs evidence dated in the current year.
    """
    now_year = int(current_year or date.today().year)
    claims = claims or []
    gaps = []

    for requirement in requirements or []:
        if requirement.get("current") is not True:
            continue
        key = _norm(requirement.get("key"))
        if not key:
            continue
        max_age = max(0, int(requirement.get("max_age_years", 0) or 0))
        matching = [c for c in claims if _norm(c.get("key")) == key and c.get("verified") is True]
        if not matching:
            continue  # no-verified-claim belongs to the sufficiency function

        years = []
        for claim in matching:
            y = _year(claim.get("effective_date")) or _year(claim.get("published_date")) or _year(claim.get("year"))
            if y is not None:
                years.append(y)

        if not years:
            gaps.append({"key": key, "reason": "missing_freshness", "scope_field": "date", "recast_hint": f"{key} current effective date"})
        elif max(years) < now_year - max_age:
            gaps.append({"key": key, "reason": "stale_evidence", "scope_field": "date", "recast_hint": f"{key} current {now_year} effective date"})

    return gaps


if __name__ == "__main__":
    req = [{"key":"bag limit", "current":True}]
    fresh = [{"key":"bag limit", "verified":True, "effective_date":"2026-03-01"}]
    assert diagnose_freshness(req, fresh, 2026) == []

    undated = [{"key":"bag limit", "verified":True}]
    g = diagnose_freshness(req, undated, 2026)
    assert len(g) == 1 and g[0]["reason"] == "missing_freshness"

    stale = [{"key":"bag limit", "verified":True, "published_date":"2024-05-01"}]
    g = diagnose_freshness(req, stale, 2026)
    assert len(g) == 1 and g[0]["reason"] == "stale_evidence" and "2026" in g[0]["recast_hint"]

    tolerant = [{"key":"bag limit", "current":True, "max_age_years":2}]
    assert diagnose_freshness(tolerant, stale, 2026) == []
    print("evidence_freshness_gap: PASS")
