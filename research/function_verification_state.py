#!/usr/bin/env python3
"""Small fail-closed state classifier for reusable research-function candidates."""

STATES = frozenset({
    "DISCOVERED",
    "TESTED",
    "VERIFIED",
    "REJECTED",
    "NEEDS-MORE-EVIDENCE",
})

REQUIRED_SPEC_FIELDS = (
    "purpose", "trigger", "input", "transformation", "output_done",
    "dependencies", "stop_rule", "failure_boundary",
)


def verification_state(record):
    """Classify without promoting uncertainty to VERIFIED."""
    if record.get("rejected") is True:
        return "REJECTED"

    discovered = record.get("discovered") is True
    tested = record.get("tests_run") is True

    if not discovered:
        return "NEEDS-MORE-EVIDENCE"
    if not tested:
        return "DISCOVERED"
    if record.get("tests_passed") is not True:
        return "REJECTED"

    if record.get("provenance_ok") is not True:
        return "NEEDS-MORE-EVIDENCE"
    if record.get("claimed_benefit_confirmed") is not True:
        return "NEEDS-MORE-EVIDENCE"
    if record.get("countertests_run") is not True:
        return "TESTED"
    if record.get("failure_boundary_recorded") is not True:
        return "TESTED"
    if any(not record.get(field) for field in REQUIRED_SPEC_FIELDS):
        return "TESTED"

    return "VERIFIED"


if __name__ == "__main__":
    good = {
        "discovered": True,
        "tests_run": True,
        "tests_passed": True,
        "provenance_ok": True,
        "claimed_benefit_confirmed": True,
        "countertests_run": True,
        "failure_boundary_recorded": True,
        "purpose": "improve recall",
        "trigger": "named evidence gap",
        "input": "query plus evidence",
        "transformation": "small search transform",
        "output_done": "measured candidate evidence",
        "dependencies": "none",
        "stop_rule": "stop on no measurable gain",
        "failure_boundary": "duplicates or same-source-family only",
    }
    assert verification_state(good) == "VERIFIED"

    cases = [
        ({}, "NEEDS-MORE-EVIDENCE"),
        ({"discovered": True}, "DISCOVERED"),
        ({**good, "countertests_run": False}, "TESTED"),
        ({**good, "provenance_ok": False}, "NEEDS-MORE-EVIDENCE"),
        ({**good, "tests_passed": False}, "REJECTED"),
        ({**good, "rejected": True}, "REJECTED"),
        ({**good, "stop_rule": ""}, "TESTED"),
    ]
    for record, expected in cases:
        assert verification_state(record) == expected, (record, expected)

    print("PASS function_verification_state")
