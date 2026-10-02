from function_candidate_state import promotion_decision


def test_only_verified_promotes():
    for state in ("DISCOVERED", "TESTED", "REJECTED", "NEEDS-MORE-EVIDENCE"):
        result = promotion_decision({"state": state})
        assert result["decision"] == "QUARANTINE", (state, result)

    assert promotion_decision({"state": "VERIFIED"})["decision"] == "PROMOTE"


def test_unknown_and_malformed_fail_closed():
    assert promotion_decision({"state": "looks-good"}) == {
        "state": "NEEDS-MORE-EVIDENCE",
        "decision": "QUARANTINE",
    }
    assert promotion_decision(None)["decision"] == "QUARANTINE"
    assert promotion_decision({})["decision"] == "QUARANTINE"


if __name__ == "__main__":
    test_only_verified_promotes()
    test_unknown_and_malformed_fail_closed()
    print("warehouse candidate state gate: PASS")
