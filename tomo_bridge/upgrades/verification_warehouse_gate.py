#!/data/data/com.termux/files/usr/bin/python
"""Small verification/warehouse gate for 3 Amigos.
Reads one V20 JSON result. Never promotes HOLD/failed output.
Promotion requires verified claims linked to valid source provenance.
Optional evidence_requirements.required_source_classes can require cross-check lanes
such as ["official", "end_user"] without welding policy into the verifier.
"""
import sys,json,hashlib
from urllib.parse import urlparse

OFFICIAL_HINTS=(".gov", ".gov.au", ".edu", "legislation.", "fisheries.", "health.", "docs.")
ENDUSER_HINTS=("reddit.com","forum","community","stackexchange.com","stackoverflow.com")
VALID_CLASSES={"official","end_user","other"}

def source_class(url):
    host=(urlparse(str(url)).hostname or "").lower()
    if any(x in host for x in OFFICIAL_HINTS): return "official"
    if any(x in host for x in ENDUSER_HINTS): return "end_user"
    return "other"

def valid_source(s):
    url=str(s.get("url") or "")
    p=urlparse(url)
    return bool(s.get("id") is not None and p.scheme in ("http","https") and p.hostname)

def required_classes(run):
    req=(run.get("evidence_requirements") or {}).get("required_source_classes") or []
    return sorted({str(x) for x in req if str(x) in VALID_CLASSES})

def verify_record(run):
    reasons=[]
    if run.get("status") != "ANSWER_READY": reasons.append("search_not_answer_ready")
    claims=run.get("verified_claims") or []
    sources=run.get("sources") or []
    valid=[s for s in sources if valid_source(s)]
    ids=[str(s.get("id")) for s in valid]
    duplicate_ids=sorted({x for x in ids if ids.count(x)>1})
    by_id={str(s.get("id")):s for s in valid}
    if not claims: reasons.append("no_verified_claims")
    if not by_id: reasons.append("no_source_provenance")
    if len(valid) != len(sources): reasons.append("invalid_source_provenance")
    if duplicate_ids: reasons.append("duplicate_source_id")
    dangling=[]
    empty_claims=[]
    for c in claims:
        text=str(c.get("text") or "").strip()
        if not text: empty_claims.append("empty")
        claim_ids=[str(i) for i in (c.get("source_ids") or [])]
        if not claim_ids or any(i not in by_id for i in claim_ids):
            dangling.append(text[:80])
    if empty_claims: reasons.append("empty_verified_claim")
    if dangling: reasons.append("claim_source_link_failed")
    classes=sorted({source_class(s.get("url")) for s in by_id.values()})
    required=required_classes(run)
    missing_classes=sorted(set(required)-set(classes))
    if missing_classes: reasons.append("required_source_class_missing")
    return {"promote":not reasons,"reasons":reasons,"source_classes":classes,
            "required_source_classes":required,"missing_source_classes":missing_classes,
            "claim_count":len(claims),"source_count":len(by_id)}

def warehouse_record(run,gate):
    compact={"question":run.get("question"),"verified_claims":run.get("verified_claims") or [],
             "sources":run.get("sources") or [],"evidence_requirements":run.get("evidence_requirements") or {},
             "verification":gate}
    raw=json.dumps(compact,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
    compact["provenance_sha256"]=hashlib.sha256(raw).hexdigest()
    compact["warehouse_status"]="VERIFIED_PROMOTABLE" if gate["promote"] else "QUARANTINE"
    return compact

def main():
    data=json.load(open(sys.argv[1],encoding="utf-8")) if len(sys.argv)>1 else json.load(sys.stdin)
    gate=verify_record(data); out=warehouse_record(data,gate)
    print(json.dumps(out,indent=2,ensure_ascii=False))
    raise SystemExit(0 if gate["promote"] else 2)

if __name__=="__main__": main()
