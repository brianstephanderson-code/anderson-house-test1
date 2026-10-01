#!/usr/bin/env python3
"""Diagnose missing claim scope before contradiction/recast.

Small deterministic function: it does not search or decide truth.  It turns
missing date/location/jurisdiction/population scope into explicit evidence gaps
that the recast layer can target.
"""

SCOPE_FIELDS = ("date", "location", "jurisdiction", "population")


def diagnose_scope_gaps(requirements, claims):
    gaps = []
    claims = claims or []
    for req in requirements or []:
        key = str(req.get("key") or "").strip().lower()
        required = [f for f in req.get("required_scope", []) if f in SCOPE_FIELDS]
        if not key or not required:
            continue
        matches = [c for c in claims if str(c.get("key") or "").strip().lower() == key]
        for field in required:
            if not any(str(c.get(field) or "").strip() for c in matches):
                gaps.append({
                    "key": key,
                    "reason": "missing_scope",
                    "scope_field": field,
                    "recast_hint": f"{key} {field}",
                })
    return gaps


if __name__ == "__main__":
    req = [{"key": "bag limit", "required_scope": ["jurisdiction", "date"]}]
    claims = [{"key": "bag limit", "jurisdiction": "Western Australia"}]
    gaps = diagnose_scope_gaps(req, claims)
    assert gaps == [{
        "key": "bag limit", "reason": "missing_scope", "scope_field": "date",
        "recast_hint": "bag limit date"
    }]
    assert diagnose_scope_gaps(req, [{"key":"bag limit", "jurisdiction":"WA", "date":"2026"}]) == []
    print("scope_gap_diagnosis: PASS")
