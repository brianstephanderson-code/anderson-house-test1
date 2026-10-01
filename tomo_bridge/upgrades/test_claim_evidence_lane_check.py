#!/data/data/com.termux/files/usr/bin/python
"""Zero-network tests for per-claim evidence lane checking."""
from claim_evidence_lane_check import claim_lane_failures
from source_provenance_classifier import classify_source

def main():
    sources={
        "o1":{"id":"o1","url":"https://example.gov.au/rule"},
        "u1":{"id":"u1","url":"https://reddit.com/r/test/x"},
    }
    required=["official","end_user"]

    failures=claim_lane_failures(
        [{"text":"cross checked","source_ids":["o1","u1"]}],
        sources,required,classify_source)
    assert failures==[], failures

    failures=claim_lane_failures(
        [{"text":"official only","source_ids":["o1"]}],
        sources,required,classify_source)
    assert len(failures)==1, failures
    assert failures[0]["missing_source_classes"]==["end_user"], failures

    failures=claim_lane_failures(
        [{"text":"end user only","source_ids":["u1"]}],
        sources,required,classify_source)
    assert failures[0]["missing_source_classes"]==["official"], failures

    # No lane policy means this small checker stays out of the way.
    assert claim_lane_failures(
        [{"text":"ordinary claim","source_ids":["o1"]}],
        sources,[],classify_source)==[]

    print("PASS: per-claim evidence lane regression suite")

if __name__=="__main__": main()
