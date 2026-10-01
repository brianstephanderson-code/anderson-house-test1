#!/data/data/com.termux/files/usr/bin/python
"""Zero-network regression tests for verification_warehouse_gate."""
from verification_warehouse_gate import verify_record, warehouse_record

def run(status="ANSWER_READY", sources=None, claims=None, required=None):
    data={"status":status,"question":"test","sources":sources or [],"verified_claims":claims or []}
    if required is not None:
        data["evidence_requirements"]={"required_source_classes":required}
    return verify_record(data), data

def main():
    official={"id":"o1","url":"https://example.gov.au/rule"}
    enduser={"id":"u1","url":"https://reddit.com/r/test/x"}
    claim={"text":"supported claim","source_ids":["o1","u1"]}
    gate,data=run(sources=[official,enduser],claims=[claim],required=["official","end_user"])
    assert gate["promote"], gate
    assert warehouse_record(data,gate)["warehouse_status"]=="VERIFIED_PROMOTABLE"

    gate,_=run(sources=[official],claims=[{"text":"claim","source_ids":["o1"]}],required=["official","end_user"])
    assert not gate["promote"] and "required_source_class_missing" in gate["reasons"], gate

    gate,_=run(status="HOLD_NEEDS_RECAST",sources=[official,enduser],claims=[claim])
    assert not gate["promote"] and "search_not_answer_ready" in gate["reasons"], gate

    gate,_=run(sources=[{"id":"x","url":"file:///tmp/not-web"}],claims=[{"text":"claim","source_ids":["x"]}])
    assert not gate["promote"] and "invalid_source_provenance" in gate["reasons"], gate

    dup=[{"id":"x","url":"https://a.gov/x"},{"id":"x","url":"https://b.gov/x"}]
    gate,_=run(sources=dup,claims=[{"text":"claim","source_ids":["x"]}])
    assert not gate["promote"] and "duplicate_source_id" in gate["reasons"], gate
    print("PASS: verification warehouse gate regression suite")

if __name__=="__main__": main()
