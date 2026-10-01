#!/usr/bin/env python3
"""Small route-coverage gate for search discovery. Standard library only.

Checks candidate diversity before FETCH without performing network work.
"""
from urllib.parse import urlsplit


def _host(row):
    return urlsplit(str(row.get("canonical_url") or row.get("url") or "")).hostname or ""


def route_coverage(rows, required_lanes=("official_candidate", "end_user"), min_hosts=3):
    """Return discovery coverage and precise gaps; never claims evidence is verified."""
    lanes = {str(r.get("source_lane") or "other") for r in rows}
    hosts = {_host(r).lower() for r in rows if _host(r)}
    missing = [lane for lane in required_lanes if lane not in lanes]
    gaps = [{"kind": "missing_lane", "lane": lane} for lane in missing]
    if len(hosts) < min_hosts:
        gaps.append({"kind": "low_host_diversity", "have": len(hosts), "need": min_hosts})
    return {
        "ready": not gaps,
        "host_count": len(hosts),
        "lanes": sorted(lanes),
        "gaps": gaps,
    }


def discovery_recasts(purpose, coverage):
    """Make only the casts needed to repair discovery coverage."""
    purpose = " ".join(str(purpose or "").split())
    casts = []
    for gap in coverage.get("gaps", []):
        if gap.get("kind") == "missing_lane" and gap.get("lane") == "official_candidate":
            casts.append(purpose + " official primary source documentation")
        elif gap.get("kind") == "missing_lane" and gap.get("lane") == "end_user":
            casts.append(purpose + " forum reddit user experience problems")
        elif gap.get("kind") == "low_host_diversity":
            casts.append(purpose + " independent sources alternatives")
    out=[]; seen=set()
    for cast in casts:
        key=cast.casefold()
        if cast and key not in seen:
            seen.add(key); out.append(cast)
    return out


if __name__ == "__main__":
    good=[
        {"url":"https://agency.gov.au/a","source_lane":"official_candidate"},
        {"url":"https://reddit.com/r/x/1","source_lane":"end_user"},
        {"url":"https://independent.example/a","source_lane":"other"},
    ]
    c=route_coverage(good)
    assert c["ready"] is True, c
    thin=[{"url":"https://agency.gov.au/a","source_lane":"official_candidate"}]
    c=route_coverage(thin)
    assert c["ready"] is False and any(g.get("lane")=="end_user" for g in c["gaps"]), c
    casts=discovery_recasts("best bait salmon WA",c)
    assert any("user experience" in q for q in casts), casts
    assert any("independent sources" in q for q in casts), casts
    print("PASS route_coverage",c,casts)
