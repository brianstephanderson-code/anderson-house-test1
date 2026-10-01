#!/usr/bin/env python3
"""Small deterministic contradiction diagnosis for Amigos reasoning/recast.
No network calls. It does not decide truth; it identifies what must be recast.
"""

def _norm(value):
    return " ".join(str(value or "").lower().split())


def diagnose_contradictions(claims):
    """Group incompatible supported values for the same normalized question/key.

    Input claim example:
      {"key":"bag limit", "value":"4", "source_lane":"official", "source_id":"s1"}
    Returns target gaps + suggested casts; search remains a separate function.
    """
    groups = {}
    for claim in claims or []:
        key = _norm(claim.get("key") or claim.get("question"))
        value = _norm(claim.get("value") or claim.get("answer"))
        if not key or not value:
            continue
        groups.setdefault(key, {}).setdefault(value, []).append(claim)

    contradictions = []
    casts = []
    gaps = []
    for key, values in groups.items():
        if len(values) < 2:
            continue
        lanes = sorted({_norm(c.get("source_lane")) for cs in values.values() for c in cs if c.get("source_lane")})
        contradictions.append({"key": key, "values": sorted(values), "source_lanes": lanes})
        gaps.append("resolve contradiction: " + key)
        casts.extend([
            f'"{key}" current official source',
            f'"{key}" effective date regulation',
            f'"{key}" end user experience conflict',
        ])

    # Stable de-duplication keeps recast history comparable.
    unique = []
    seen = set()
    for cast in casts:
        n = _norm(cast)
        if n not in seen:
            seen.add(n)
            unique.append(cast)
    return {
        "has_contradiction": bool(contradictions),
        "contradictions": contradictions,
        "target_gaps": gaps,
        "suggested_casts": unique,
    }


if __name__ == "__main__":
    clean = diagnose_contradictions([
        {"key":"best bait", "value":"pilchard", "source_lane":"end_user"},
        {"key":"best bait", "value":"pilchard", "source_lane":"official"},
    ])
    assert not clean["has_contradiction"]
    conflict = diagnose_contradictions([
        {"key":"bag limit", "value":"4", "source_lane":"official"},
        {"key":"bag limit", "value":"2", "source_lane":"end_user"},
    ])
    assert conflict["has_contradiction"]
    assert conflict["target_gaps"] == ["resolve contradiction: bag limit"]
    assert len(conflict["suggested_casts"]) == 3
    print("contradiction_diagnosis: PASS")
