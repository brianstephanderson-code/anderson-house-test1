#!/usr/bin/env python3
"""Small reusable lane-balancing step for ranked search candidates.

Input rows are already relevance-ranked. This function does not decide truth or
authority; it only ensures required discovery lanes get a fair chance to be read.
Standard library only; zero network calls.
"""

def lane_balanced_rank(rows, budget=8, required_lanes=("official_candidate", "end_user")):
    """Preserve relevance as much as possible while reserving one slot per required lane.

    Rows should contain ``source_lane``. Missing lanes are reported explicitly so
    the caller can recast instead of silently pretending discovery was diverse.
    Returns (selected, missing_lanes).
    """
    if budget <= 0:
        return [], list(required_lanes)

    rows = list(rows)
    selected = []
    used = set()
    missing = []

    # First take the highest-ranked candidate from each required evidence lane.
    for lane in required_lanes:
        hit = next(((i, row) for i, row in enumerate(rows)
                    if i not in used and row.get("source_lane") == lane), None)
        if hit is None:
            missing.append(lane)
            continue
        i, row = hit
        selected.append(row)
        used.add(i)
        if len(selected) >= budget:
            return selected, missing

    # Fill remaining budget in original relevance order.
    for i, row in enumerate(rows):
        if i in used:
            continue
        selected.append(row)
        if len(selected) >= budget:
            break
    return selected, missing


def discovery_recast_hints(missing_lanes, query):
    """Turn missing discovery lanes into small, explicit recast hints."""
    hints = []
    q = str(query or "").strip()
    if "official_candidate" in missing_lanes:
        hints.append({"lane": "official_candidate", "cast": q + " official guidance"})
    if "end_user" in missing_lanes:
        hints.append({"lane": "end_user", "cast": q + " forum community experience"})
    return hints


if __name__ == "__main__":
    rows = [
        {"title": "A", "source_lane": "other"},
        {"title": "B", "source_lane": "other"},
        {"title": "C", "source_lane": "end_user"},
        {"title": "D", "source_lane": "official_candidate"},
        {"title": "E", "source_lane": "other"},
    ]
    got, missing = lane_balanced_rank(rows, budget=4)
    assert not missing, missing
    assert {x["source_lane"] for x in got} >= {"official_candidate", "end_user"}
    assert len(got) == 4

    got2, missing2 = lane_balanced_rank(rows[:3], budget=3)
    assert missing2 == ["official_candidate"], missing2
    hints = discovery_recast_hints(missing2, "salmon bait WA")
    assert hints == [{"lane": "official_candidate", "cast": "salmon bait WA official guidance"}]
    print("PASS lane_balanced_rank", [x["title"] for x in got], missing2)
