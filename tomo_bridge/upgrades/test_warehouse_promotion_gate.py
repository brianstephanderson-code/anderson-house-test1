#!/data/data/com.termux/files/usr/bin/python
"""Zero-network regression tests for warehouse_promotion_gate."""

from warehouse_promotion_gate import warehouse_promotion_decision


def test_promotes_only_clean_verified_tested_work():
    result = warehouse_promotion_decision(test_results=[{"name": "smoke", "passed": True}])
    assert result == {"decision": "PROMOTE", "reasons": []}


def test_missing_tests_fail_closed():
    result = warehouse_promotion_decision()
    assert result["decision"] == "QUARANTINE"
    assert "TESTS_NOT_RUN" in result["reasons"]


def test_unknown_test_is_not_a_pass():
    result = warehouse_promotion_decision(test_results=[{"name": "phone", "passed": None}])
    assert result["decision"] == "QUARANTINE"
    assert "TEST_FAILED_OR_UNKNOWN" in result["reasons"]


def test_provenance_and_lane_failures_are_preserved():
    result = warehouse_promotion_decision(
        reference_failures=[{"claim_index": 0}],
        lane_failures=[{"claim_index": 1}],
        test_results=[{"name": "smoke", "passed": True}],
    )
    assert result["decision"] == "QUARANTINE"
    assert result["reasons"] == [
        "BROKEN_SOURCE_PROVENANCE",
        "MISSING_REQUIRED_EVIDENCE_LANE",
    ]


if __name__ == "__main__":
    test_promotes_only_clean_verified_tested_work()
    test_missing_tests_fail_closed()
    test_unknown_test_is_not_a_pass()
    test_provenance_and_lane_failures_are_preserved()
    print("warehouse promotion gate: PASS")
