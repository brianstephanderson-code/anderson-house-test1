#!/usr/bin/env python3
"""Small deterministic SUFFICIENT? gate for Amigos reasoning.

Checks verified claim coverage, required evidence lanes, and unresolved
contradictions. It diagnoses gaps only; search/recast remain separate functions.
"""


def _norm(value):
    return " ".join(str(value or "").lower().split())


def assess_sufficiency(requirements, claims, contradictions=None):
    """Return an explicit sufficiency decision and machine-readable gaps.

    requirement example:
      {"key":"bag limit", "required_lanes":["official"]}
    claim example:
      {"key":"bag limit", "verified":True, "source_lane":"official"}
    contradiction example:
      {"key":"bag limit", "resolved":False}
    """
    gaps = []
    claims = claims or []

    for requirement in requirements or []:
        key = _norm(requirement.get("key"))
        if not key:
            continue
        required_lanes = {_norm(x) for x in requirement.get("required_lanes", []) if _norm(x)}
        matches = [
            claim for claim in claims
            if _norm(claim.get("key")) == key and claim.get("verified") is True
        ]
        if not matches:
            gaps.append({
                "key": key,
                "reason": "no_verified_claim",
                "missing_lanes": sorted(required_lanes),
            })
            continue

        present_lanes = {_norm(c.get("source_lane")) for c in matches if _norm(c.get("source_lane"))}
        missing_lanes = required_lanes - present_lanes
        if missing_lanes:
            gaps.append({
                "key": key,
                "reason": "missing_required_lane",
                "missing_lanes": sorted(missing_lanes),
            })

    for contradiction in contradictions or []:
        if contradiction.get("resolved") is True:
            continue
        key = _norm(contradiction.get("key"))
        if key and not any(g["key"] == key and g["reason"] == "unresolved_contradiction" for g in gaps):
            gaps.append({"key": key, "reason": "unresolved_contradiction", "missing_lanes": []})

    return {
        "sufficient": not bool(gaps),
        "gaps": gaps,
        "verified_claim_count": sum(1 for c in claims if c.get("verified") is True),
    }


if __name__ == "__main__":
    good = assess_sufficiency(
        [{"key":"bag limit", "required_lanes":["official"]}],
        [{"key":"bag limit", "verified":True, "source_lane":"official"}],
    )
    assert good["sufficient"]

    lane_gap = assess_sufficiency(
        [{"key":"best bait", "required_lanes":["official", "end_user"]}],
        [{"key":"best bait", "verified":True, "source_lane":"official"}],
    )
    assert not lane_gap["sufficient"]
    assert lane_gap["gaps"][0]["missing_lanes"] == ["end_user"]

    conflict = assess_sufficiency([], [], [{"key":"bag limit", "resolved":False}])
    assert not conflict["sufficient"]
    assert conflict["gaps"][0]["reason"] == "unresolved_contradiction"
    print("evidence_sufficiency: PASS")
