#!/usr/bin/env python3
"""Fail-closed useful-gain check for Amigos recast loops.

Small adapter only: compare verified before/after snapshots. It does not search,
rank, fetch, or decide truth.
"""


def _ids(value):
    return {str(x).strip() for x in (value or []) if str(x).strip()}


def recast_evidence_gain(previous, current):
    previous, current = previous or {}, current or {}

    old_gaps = _ids(previous.get("target_gaps"))
    new_gaps = _ids(current.get("target_gaps"))
    old_claims = _ids(previous.get("verified_claim_ids"))
    new_claims = _ids(current.get("verified_claim_ids"))
    old_families = _ids(previous.get("verified_source_families"))
    new_families = _ids(current.get("verified_source_families"))
    old_resolved = _ids(previous.get("resolved_contradiction_ids"))
    new_resolved = _ids(current.get("resolved_contradiction_ids"))
    old_known = _ids(previous.get("known_answer_ids"))
    new_known = _ids(current.get("known_answer_ids"))

    closed_gaps = sorted(old_gaps - new_gaps)
    gained_claims = sorted(new_claims - old_claims)
    gained_families = sorted(new_families - old_families)
    resolved = sorted(new_resolved - old_resolved)
    recovered_known = sorted(new_known - old_known)

    reasons = []
    if closed_gaps:
        reasons.append("closed_gap")
    if gained_claims:
        reasons.append("new_verified_claim")
    if gained_families:
        reasons.append("new_verified_source_family")
    if resolved:
        reasons.append("resolved_contradiction")
    if recovered_known:
        reasons.append("recovered_known_answer")

    return {
        "progressed": bool(reasons),
        "reasons": reasons,
        "closed_gaps": closed_gaps,
        "gained_verified_claim_ids": gained_claims,
        "gained_verified_source_families": gained_families,
        "resolved_contradiction_ids": resolved,
        "recovered_known_answer_ids": recovered_known,
    }


if __name__ == "__main__":
    before = {
        "target_gaps": ["official", "independent"],
        "verified_claim_ids": ["c1"],
        "verified_source_families": ["gov"],
        "resolved_contradiction_ids": [],
        "known_answer_ids": [],
    }

    # More fetched material alone is deliberately invisible here: only verified
    # evidence signals can keep a recast alive.
    noise = dict(before)
    noise["source_ids"] = ["s1", "s2", "s3"]
    assert not recast_evidence_gain(before, noise)["progressed"]

    diverse = dict(before)
    diverse["verified_source_families"] = ["gov", "forum"]
    assert recast_evidence_gain(before, diverse)["reasons"] == ["new_verified_source_family"]

    closed = dict(before)
    closed["target_gaps"] = ["independent"]
    assert "closed_gap" in recast_evidence_gain(before, closed)["reasons"]

    known = dict(before)
    known["known_answer_ids"] = ["answer-1"]
    assert "recovered_known_answer" in recast_evidence_gain(before, known)["reasons"]

    contradiction = dict(before)
    contradiction["resolved_contradiction_ids"] = ["x1"]
    assert "resolved_contradiction" in recast_evidence_gain(before, contradiction)["reasons"]

    print("recast_evidence_gain: PASS")
