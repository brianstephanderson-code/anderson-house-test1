#!/usr/bin/env python3
"""Translate SUFFICIENT? gaps into targeted recast instructions.

Small adapter only: it does not search, rank, fetch, or decide truth.
"""


def _clean(value):
    return " ".join(str(value or "").split())


def gap_to_recasts(question, gap):
    """Return lane-specific recast intents from evidence/scope gaps."""
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
    elif reason == "missing_scope":
        field = _clean((gap or {}).get("scope_field"))
        hint = _clean((gap or {}).get("recast_hint"))
        target = hint or _clean(f"{key} {field}")
        if target:
            out.append({"lane": "official", "gap": key, "query": _clean(f"{question} {target} official current primary source")})
    elif reason in ("missing_freshness", "stale_evidence"):
        hint = _clean((gap or {}).get("recast_hint")) or _clean(f"{key} current effective date")
        out.append({"lane": "official", "gap": key, "query": _clean(f"{question} {hint} official current primary source")})
    elif reason in ("missing_independence", "insufficient_independent_sources"):
        hint = _clean((gap or {}).get("recast_hint")) or _clean(f"{key} independent corroboration")
        out.append({"lane": "independent", "gap": key, "query": _clean(f"{question} {hint} different source independent evidence comparison")})
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
    scope = gap_to_recasts("salmon bag limit", {"key":"bag limit", "reason":"missing_scope", "scope_field":"date", "recast_hint":"bag limit date"})
    assert len(scope) == 1 and scope[0]["lane"] == "official" and "bag limit date" in scope[0]["query"]
    empty_scope = gap_to_recasts("salmon bag limit", {"key":"bag limit", "reason":"missing_scope"})
    assert len(empty_scope) == 1 and "bag limit" in empty_scope[0]["query"]
    stale = gap_to_recasts("salmon bag limit WA", {"key":"bag limit", "reason":"stale_evidence", "recast_hint":"bag limit current 2026 effective date"})
    assert len(stale) == 1 and stale[0]["lane"] == "official" and "2026" in stale[0]["query"]
    independent = gap_to_recasts("salmon bag limit WA", {"key":"bag limit", "reason":"insufficient_independent_sources", "recast_hint":"find a different source family"})
    assert len(independent) == 1 and independent[0]["lane"] == "independent" and "different source" in independent[0]["query"]
    print("gap_to_recast: PASS")
