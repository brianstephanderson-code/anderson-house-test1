"""Fail-closed verification state gate for reusable function candidates.

Small warehouse building block: promotion is allowed only from VERIFIED.
This module deliberately does not decide whether evidence is true; upstream
verification/testing does that. It prevents DISCOVERED/TESTED/REJECTED/
NEEDS-MORE-EVIDENCE candidates from being accidentally promoted.
"""

ALLOWED_STATES = frozenset({
    "DISCOVERED",
    "TESTED",
    "VERIFIED",
    "REJECTED",
    "NEEDS-MORE-EVIDENCE",
})


def normalize_state(value):
    if not isinstance(value, str):
        return "NEEDS-MORE-EVIDENCE"
    state = value.strip().upper().replace("_", "-")
    return state if state in ALLOWED_STATES else "NEEDS-MORE-EVIDENCE"


def promotion_decision(candidate):
    """Return PROMOTE only for explicitly VERIFIED candidates; otherwise quarantine."""
    if not isinstance(candidate, dict):
        return {"state": "NEEDS-MORE-EVIDENCE", "decision": "QUARANTINE"}
    state = normalize_state(candidate.get("state"))
    return {
        "state": state,
        "decision": "PROMOTE" if state == "VERIFIED" else "QUARANTINE",
    }
