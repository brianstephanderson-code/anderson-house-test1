#!/usr/bin/env python3
"""Small deterministic guard against near-duplicate recast loops.

It normalizes search boilerplate and compares meaningful query tokens.
It does not search, rank, fetch, or decide truth.
"""
import re

_BOILERPLATE = {
    "official", "current", "primary", "source", "sources", "evidence",
    "user", "users", "experience", "experiences", "forum", "discussion",
    "independent", "compare", "conflicting", "reports", "report",
}


def _tokens(query):
    words = re.findall(r"[a-z0-9]+", str(query or "").lower())
    return {w for w in words if len(w) > 1 and w not in _BOILERPLATE}


def similarity(a, b):
    """Jaccard similarity over meaningful recast tokens."""
    left, right = _tokens(a), _tokens(b)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def assess_recast_novelty(candidate, previous_queries, threshold=0.85):
    """Return whether candidate materially differs from previous recasts."""
    best_query, best_score = "", 0.0
    for previous in previous_queries or []:
        score = similarity(candidate, previous)
        if score > best_score:
            best_query, best_score = str(previous or ""), score
    novel = bool(_tokens(candidate)) and best_score < threshold
    return {
        "novel": novel,
        "best_similarity": round(best_score, 3),
        "nearest_previous": best_query,
        "action": "RECAST" if novel else "CHANGE_STRATEGY_OR_STOP",
    }


if __name__ == "__main__":
    same = assess_recast_novelty(
        "bag limit WA official current primary source",
        ["bag limit WA official primary source evidence"],
    )
    assert not same["novel"] and same["action"] == "CHANGE_STRATEGY_OR_STOP"

    changed = assess_recast_novelty(
        "bag limit WA regulation effective date 2026",
        ["bag limit WA user experience forum discussion"],
    )
    assert changed["novel"] and changed["action"] == "RECAST"

    empty = assess_recast_novelty("official evidence", [])
    assert not empty["novel"]
    print("recast_novelty: PASS")
