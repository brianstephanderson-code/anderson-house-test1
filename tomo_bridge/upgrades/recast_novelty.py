#!/usr/bin/env python3
"""Small deterministic guard against near-duplicate recast loops.

A recast is novel when it changes either meaningful subject terms or the
evidence lane/strategy. It does not search, rank, fetch, or decide truth.
"""
import re

_BOILERPLATE = {
    "current", "source", "sources", "evidence", "experience", "experiences",
    "discussion", "compare", "conflicting", "reports", "report",
}
_LANE_MARKERS = {
    "official": {"official", "primary", "regulation", "policy"},
    "end_user": {"user", "users", "forum", "community", "operator"},
    "independent": {"independent", "review", "analysis", "third", "party"},
}


def _words(query):
    return set(re.findall(r"[a-z0-9]+", str(query or "").lower()))


def _lanes(query):
    words = _words(query)
    return {lane for lane, markers in _LANE_MARKERS.items() if words & markers}


def _tokens(query):
    lane_words = set().union(*_LANE_MARKERS.values())
    return {w for w in _words(query) if len(w) > 1 and w not in _BOILERPLATE and w not in lane_words}


def similarity(a, b):
    """Jaccard similarity over meaningful subject tokens."""
    left, right = _tokens(a), _tokens(b)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def assess_recast_novelty(candidate, previous_queries, threshold=0.85):
    """Return whether candidate materially differs from previous recasts.

    Changing evidence lane counts as a real strategy change even when the
    subject words are identical. This prevents an official-source search from
    suppressing a later end-user or independent cross-check.
    """
    candidate_tokens = _tokens(candidate)
    candidate_lanes = _lanes(candidate)
    if not candidate_tokens:
        return {"novel": False, "best_similarity": 0.0, "nearest_previous": "", "lane_change": False, "action": "CHANGE_STRATEGY_OR_STOP"}

    best_query, best_score = "", 0.0
    lane_change = False
    for previous in previous_queries or []:
        score = similarity(candidate, previous)
        same_subject = score >= threshold
        changed_lane = bool(candidate_lanes) and candidate_lanes != _lanes(previous)
        if same_subject and changed_lane:
            lane_change = True
        if score > best_score:
            best_query, best_score = str(previous or ""), score

    novel = lane_change or best_score < threshold
    return {
        "novel": novel,
        "best_similarity": round(best_score, 3),
        "nearest_previous": best_query,
        "lane_change": lane_change,
        "action": "RECAST" if novel else "CHANGE_STRATEGY_OR_STOP",
    }


if __name__ == "__main__":
    same = assess_recast_novelty(
        "bag limit WA official current primary source",
        ["bag limit WA official primary source evidence"],
    )
    assert not same["novel"] and same["action"] == "CHANGE_STRATEGY_OR_STOP"

    # Same subject, genuinely different evidence lane: must not be suppressed.
    lane_switch = assess_recast_novelty(
        "bag limit WA user experience forum discussion",
        ["bag limit WA official primary source evidence"],
    )
    assert lane_switch["novel"] and lane_switch["lane_change"]

    changed = assess_recast_novelty(
        "bag limit WA regulation effective date 2026",
        ["bag limit WA user experience forum discussion"],
    )
    assert changed["novel"] and changed["action"] == "RECAST"

    empty = assess_recast_novelty("official evidence", [])
    assert not empty["novel"]
    print("recast_novelty: PASS")
