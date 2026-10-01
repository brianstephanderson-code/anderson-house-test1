#!/usr/bin/env python3
"""Small fail-closed comparability guard for contradiction diagnosis.

Different answers are only a contradiction when they answer the same scoped
question. This function keeps scope checking separate from truth diagnosis.
No network calls.
"""


def _norm(value):
    return " ".join(str(value or "").lower().split())


def claim_scope(claim):
    """Return normalized scope fields that materially change an answer."""
    claim = claim or {}
    return {
        "key": _norm(claim.get("key") or claim.get("question")),
        "jurisdiction": _norm(claim.get("jurisdiction")),
        "location": _norm(claim.get("location")),
        "effective_date": _norm(claim.get("effective_date") or claim.get("date")),
        "population": _norm(claim.get("population") or claim.get("subject")),
    }


def compare_claims(left, right):
    """Say whether two claims are safe to compare as possible contradictions.

    Missing scope is UNKNOWN rather than silently treated as equal.  This avoids
    false contradictions and tells RECAST exactly which scope evidence is absent.
    """
    a, b = claim_scope(left), claim_scope(right)
    if not a["key"] or not b["key"] or a["key"] != b["key"]:
        return {"comparable": False, "reason": "different_key", "missing_scope": []}

    missing = []
    different = []
    for field in ("jurisdiction", "location", "effective_date", "population"):
        av, bv = a[field], b[field]
        if bool(av) != bool(bv):
            missing.append(field)
        elif av and bv and av != bv:
            different.append(field)

    if different:
        return {"comparable": False, "reason": "different_scope", "different_scope": different, "missing_scope": missing}
    if missing:
        return {"comparable": False, "reason": "scope_unknown", "missing_scope": missing}
    return {"comparable": True, "reason": "same_scope", "missing_scope": []}


if __name__ == "__main__":
    base = {"key":"bag limit", "jurisdiction":"WA", "location":"Perth", "effective_date":"2026", "population":"recreational"}
    same = dict(base, value="4")
    other_value = dict(base, value="2")
    assert compare_claims(same, other_value)["comparable"] is True

    old = dict(base, effective_date="2025", value="4")
    assert compare_claims(old, other_value)["reason"] == "different_scope"

    undated = {k:v for k,v in same.items() if k != "effective_date"}
    result = compare_claims(undated, other_value)
    assert result["reason"] == "scope_unknown"
    assert result["missing_scope"] == ["effective_date"]

    assert compare_claims({"key":"bag limit"}, {"key":"best bait"})["reason"] == "different_key"
    print("claim_comparability: PASS")
