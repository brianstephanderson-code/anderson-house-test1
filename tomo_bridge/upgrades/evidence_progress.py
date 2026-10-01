#!/usr/bin/env python3
"""Small deterministic evidence-progress scorer for Amigos recast loops."""

def _ids(items):
    return {str(x).strip() for x in (items or []) if str(x).strip()}


def measure_progress(previous, current):
    """Measure useful evidence change without deciding truth or doing search."""
    previous, current = previous or {}, current or {}
    old_sources, new_sources = _ids(previous.get("source_ids")), _ids(current.get("source_ids"))
    old_claims, new_claims = _ids(previous.get("verified_claim_ids")), _ids(current.get("verified_claim_ids"))
    old_gaps, new_gaps = _ids(previous.get("target_gaps")), _ids(current.get("target_gaps"))

    gained_sources = sorted(new_sources - old_sources)
    gained_claims = sorted(new_claims - old_claims)
    closed_gaps = sorted(old_gaps - new_gaps)
    opened_gaps = sorted(new_gaps - old_gaps)
    progressed = bool(gained_sources or gained_claims or closed_gaps)

    return {
        "progressed": progressed,
        "gained_source_ids": gained_sources,
        "gained_verified_claim_ids": gained_claims,
        "closed_gaps": closed_gaps,
        "opened_gaps": opened_gaps,
    }


if __name__ == "__main__":
    before = {"source_ids":["s1"], "verified_claim_ids":["c1"], "target_gaps":["date","limit"]}
    after = {"source_ids":["s1","s2"], "verified_claim_ids":["c1"], "target_gaps":["limit"]}
    result = measure_progress(before, after)
    assert result["progressed"]
    assert result["gained_source_ids"] == ["s2"]
    assert result["closed_gaps"] == ["date"]
    assert not measure_progress(before, before)["progressed"]
    print("evidence_progress: PASS")
