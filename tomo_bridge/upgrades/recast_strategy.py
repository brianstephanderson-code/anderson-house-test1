#!/usr/bin/env python3
"""Small deterministic recast planner: evidence gap -> changed search strategy."""
from urllib.parse import urlparse


def _clean(value):
    return " ".join(str(value or "").split())


def plan_recast(question, gap, tried_queries=None, evidence_hosts=None):
    """Return distinct recast candidates without performing search or deciding truth."""
    question, gap = _clean(question), _clean(gap)
    tried = {_clean(x).lower() for x in (tried_queries or [])}
    hosts = {urlparse(x).netloc.lower() if "://" in str(x) else str(x).lower() for x in (evidence_hosts or [])}

    casts = [
        {"lane":"official", "query":f'{question} {gap} official current policy evidence'},
        {"lane":"end_user", "query":f'{question} {gap} experience forum discussion'},
        {"lane":"independent", "query":f'{question} {gap} independent source evidence'},
    ]
    if hosts:
        casts.append({"lane":"route_change", "query":f'{question} {gap} alternative source'})

    fresh, seen = [], set()
    for cast in casts:
        key = _clean(cast["query"]).lower()
        if key and key not in tried and key not in seen:
            seen.add(key)
            fresh.append(cast)

    return {
        "gap": gap,
        "fresh_casts": fresh,
        "stop": not bool(fresh),
        "stop_reason": "all deterministic recasts already tried" if not fresh else None,
    }


if __name__ == "__main__":
    r = plan_recast("best bait for salmon WA May", "seasonal effectiveness")
    assert not r["stop"] and len(r["fresh_casts"]) == 3
    first = r["fresh_casts"][0]["query"]
    r2 = plan_recast("best bait for salmon WA May", "seasonal effectiveness", [first])
    assert len(r2["fresh_casts"]) == 2
    all_q = [x["query"] for x in r["fresh_casts"]]
    assert plan_recast("best bait for salmon WA May", "seasonal effectiveness", all_q)["stop"]
    print("recast_strategy: PASS")
