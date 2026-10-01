#!/usr/bin/env python3
"""Small deterministic selector: choose which evidence gap to recast first."""


def _clean(value):
    return " ".join(str(value or "").split())


def prioritize_gaps(gaps, contradictions=None, required_lanes=None, present_lanes=None):
    """Rank missing evidence without searching or deciding truth.

    Priority: unresolved contradiction > required missing evidence lane > ordinary gap.
    Keeps the function separate from query generation and sufficiency decisions.
    """
    contradictions = {_clean(x).lower() for x in (contradictions or []) if _clean(x)}
    required = {_clean(x).lower() for x in (required_lanes or []) if _clean(x)}
    present = {_clean(x).lower() for x in (present_lanes or []) if _clean(x)}

    ranked, seen = [], set()
    for gap in gaps or []:
        text = _clean(gap)
        key = text.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        score, reason = 10, "ordinary evidence gap"
        if key in contradictions:
            score, reason = 100, "unresolved contradiction"
        elif key in (required - present):
            score, reason = 80, "required evidence lane missing"
        ranked.append({"gap": text, "priority": score, "reason": reason})

    # Required lanes may be absent from the supplied gap list; make them explicit.
    for lane in sorted(required - present):
        if lane not in seen:
            ranked.append({"gap": lane, "priority": 80, "reason": "required evidence lane missing"})

    ranked.sort(key=lambda x: (-x["priority"], x["gap"].lower()))
    return {"ranked_gaps": ranked, "next_gap": ranked[0]["gap"] if ranked else None}


if __name__ == "__main__":
    r = prioritize_gaps(
        ["season", "official", "bait effectiveness", "season"],
        contradictions=["bait effectiveness"],
        required_lanes=["official", "end_user"],
        present_lanes=["end_user"],
    )
    assert r["next_gap"] == "bait effectiveness"
    assert [x["gap"] for x in r["ranked_gaps"]].count("season") == 1
    assert any(x["gap"] == "official" and x["priority"] == 80 for x in r["ranked_gaps"])
    r2 = prioritize_gaps([], required_lanes=["official"], present_lanes=[])
    assert r2["next_gap"] == "official"
    assert prioritize_gaps([])["next_gap"] is None
    print("recast_priority: PASS")
