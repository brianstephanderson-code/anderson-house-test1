#!/data/data/com.termux/files/usr/bin/python
"""Small fail-closed warehouse promotion gate for 3 Amigos.

This function does not fetch, classify, test, or move artifacts. It only turns
upstream verification/test results into a promotion decision, preserving small
replaceable functions and an explicit failure boundary.
"""


def warehouse_promotion_decision(reference_failures=None,
                                 lane_failures=None,
                                 verification_failures=None,
                                 test_results=None):
    """Return PROMOTE only when every supplied boundary explicitly passes.

    test_results must be a non-empty iterable of mappings with passed=True.
    Missing/unknown test state fails closed so untested work cannot enter the
    verified warehouse accidentally.
    """
    reasons = []

    if reference_failures:
        reasons.append("BROKEN_SOURCE_PROVENANCE")
    if lane_failures:
        reasons.append("MISSING_REQUIRED_EVIDENCE_LANE")
    if verification_failures:
        reasons.append("VERIFICATION_FAILED")

    tests = list(test_results or [])
    if not tests:
        reasons.append("TESTS_NOT_RUN")
    elif any(result.get("passed") is not True for result in tests):
        reasons.append("TEST_FAILED_OR_UNKNOWN")

    return {
        "decision": "PROMOTE" if not reasons else "QUARANTINE",
        "reasons": reasons,
    }
