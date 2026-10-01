#!/usr/bin/env python3
"""Small deterministic stop-rule function for Amigos recast loops.
No network calls; safe to unit-test independently.
"""

def normalize_cast(text):
    return " ".join(str(text or "").lower().split())


def decide_recast(history, diagnosis, max_rounds=3):
    """Return RECAST or STOP_* without performing search itself."""
    history = history or []
    diagnosis = diagnosis or {}
    if diagnosis.get("sufficient"):
        return {"action": "STOP_SUFFICIENT", "reason": "evidence_sufficient"}
    if len(history) >= max_rounds:
        return {"action": "STOP_BUDGET", "reason": "max_recast_rounds_reached"}

    suggested = diagnosis.get("suggested_casts") or []
    seen = {normalize_cast(c) for round_ in history for c in (round_.get("casts") or [])}
    fresh = [c for c in suggested if normalize_cast(c) and normalize_cast(c) not in seen]
    if not fresh:
        return {"action": "STOP_NO_NEW_CAST", "reason": "recast_would_repeat_previous_search"}

    previous_gaps = set(history[-1].get("target_gaps") or []) if history else set()
    current_gaps = set(diagnosis.get("target_gaps") or [])
    if history and current_gaps and current_gaps == previous_gaps:
        previous_sources = int(history[-1].get("readable_evidence_count") or 0)
        current_sources = int(diagnosis.get("readable_evidence_count") or 0)
        if current_sources <= previous_sources:
            return {"action": "STOP_NO_PROGRESS", "reason": "same_gap_without_new_evidence"}

    return {"action": "RECAST", "casts": fresh[:6], "reason": "fresh_targeted_cast_available"}


if __name__ == "__main__":
    # Cheap self-test: sufficient, duplicate, budget, and fresh-cast paths.
    assert decide_recast([], {"sufficient": True})["action"] == "STOP_SUFFICIENT"
    h=[{"casts":["q official"],"target_gaps":["date"],"readable_evidence_count":2}]
    assert decide_recast(h,{"sufficient":False,"suggested_casts":["q official"],"target_gaps":["date"]})["action"] == "STOP_NO_NEW_CAST"
    assert decide_recast([{}, {}, {}],{"sufficient":False,"suggested_casts":["new"]})["action"] == "STOP_BUDGET"
    assert decide_recast([],{"sufficient":False,"suggested_casts":["q primary source"]})["action"] == "RECAST"
    print("recast_stop_rules: PASS")
