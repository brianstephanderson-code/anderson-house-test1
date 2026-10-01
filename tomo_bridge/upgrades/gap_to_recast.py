#!/usr/bin/env python3
"""Translate SUFFICIENT? gaps into targeted recast instructions.

Small adapter only: it does not search, rank, fetch, or decide truth.
"""


def _clean(value):
    return " ".join(str(value or "").split())


def gap_to_recasts(question, gap):
    """Return lane-specific recast intents from an evidence_sufficiency gap."""
    question = _clean(question)
    key = _clean((gap or {}).get("key"))
    reason = _clean((gap or {}).get("reason"))
    missing = [_clean(x) for x in (gap or {}).get("missing_lanes", []) if _clean(x)]
    base = _clean(f"{question} {key}")
    out = []

    if reason == "missing_required_lane":
        for lane in missing:
            if lane == "official":
                out.append({"lane": lane, "gap": key, "query": f"{base} official current primary source"})
            elif lane == "end_user":
                out.append({"lane": lane, "gap": key, "query": f"{base} user experience forum discussion problems"})
            else:
                out.append({"lane": lane, "gap": key, "query": f"{base} {lane} evidence"})
    elif reason == "unresolved_contradiction":
        out.extend([
            {"lane": "official", "gap": key, "query": f"{base} official current effective date policy"},
            {"lane": "independent", "gap": key, "query": f"{base} conflicting reports compare evidence"},
            {"lane": "end_user", "gap": key, "query": f"{base} user reports changed outdated experience"},
        ])
    elif reason == "no_verified_claim":
        lanes = missing or ["official", "independent"]
        for lane in lanes:
            suffix = "official primary source" if lane == "official" else f"{lane} evidence"
            out.append({"lane": lane, "gap": key, "query": f"{base} {suffix}"})

    # deterministic anti-duplication
    seen, fresh = set(), []
    for item in out:
        q = _clean(item["query"])
        k = q.lower()
        if q and k not in seen:
            seen.add(k)
            item["query"] = q
            fresh.append(item)
    return fresh


if __name__ == "__main__":
    lane = gap_to_recasts("best bait salmon WA", {"key":"best bait", "reason":"missing_required_lane", "missing_lanes":["end_user"]})
    assert len(lane) == 1 and lane[0]["lane"] == "end_user"
    conflict = gap_to_recasts("bag limit WA", {"key":"bag limit", "reason":"unresolved_contradiction", "missing_lanes":[]})
    assert [x["lane"] for x in conflict] == ["official", "independent", "end_user"]
    absent = gap_to_recasts("bag limit WA", {"key":"bag limit", "reason":"no_verified_claim", "missing_lanes":["official"]})
    assert len(absent) == 1 and absent[0]["lane"] == "official"
    print("gap_to_recast: PASS")
