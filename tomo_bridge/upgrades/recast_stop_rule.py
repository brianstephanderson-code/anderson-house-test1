#!/usr/bin/env python3
"""Small deterministic stop rule for Amigos recast loops.

Consumes sufficiency and per-attempt progress decisions. It does not search,
judge evidence, or reformulate queries.
"""


def decide_recast_stop(attempts, sufficient=False, max_attempts=6, max_no_progress=2):
    """Choose RECAST, strategy change/stop, or a terminal stop reason.

    Only an explicit progressed=False counts as a failed recast. Missing/unknown
    progress is not evidence of failure and therefore breaks the failure streak.
    """
    attempts = attempts or []
    max_attempts = max(1, int(max_attempts))
    max_no_progress = max(1, int(max_no_progress))

    if sufficient:
        return {"action": "STOP_SUFFICIENT", "attempts": len(attempts), "no_progress_streak": 0}

    if len(attempts) >= max_attempts:
        return {"action": "STOP_BUDGET", "attempts": len(attempts), "no_progress_streak": 0}

    no_progress_streak = 0
    for attempt in reversed(attempts):
        progressed = (attempt or {}).get("progressed")
        if progressed is not False:
            break
        no_progress_streak += 1

    if no_progress_streak >= max_no_progress:
        action = "CHANGE_STRATEGY_OR_STOP"
    else:
        action = "RECAST"

    return {
        "action": action,
        "attempts": len(attempts),
        "no_progress_streak": no_progress_streak,
    }


if __name__ == "__main__":
    assert decide_recast_stop([], sufficient=True)["action"] == "STOP_SUFFICIENT"
    stalled = decide_recast_stop([{"progressed": False}, {"progressed": False}])
    assert stalled["action"] == "CHANGE_STRATEGY_OR_STOP" and stalled["no_progress_streak"] == 2
    recovered = decide_recast_stop([{"progressed": False}, {"progressed": True}, {"progressed": False}])
    assert recovered["action"] == "RECAST" and recovered["no_progress_streak"] == 1
    unknown = decide_recast_stop([{"progressed": False}, {}, {"progressed": False}])
    assert unknown["action"] == "RECAST" and unknown["no_progress_streak"] == 1
    assert decide_recast_stop([{"progressed": True}] * 6)["action"] == "STOP_BUDGET"
    print("recast_stop_rule: PASS")
