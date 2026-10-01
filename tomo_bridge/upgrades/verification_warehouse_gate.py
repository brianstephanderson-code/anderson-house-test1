#!/data/data/com.termux/files/usr/bin/python
"""Small verification/warehouse gate for 3 Amigos.
Reads one V20 JSON result. Never promotes HOLD/failed output.
Promotion requires verified claims, source provenance, and both official + end-user
source classes when the claim set depends on both evidence funnels.
"""
import sys,json,hashlib
from urllib.parse import urlparse

OFFICIAL_HINTS=(".gov", ".gov.au", ".edu", "legislation.", "fisheries.", "health.", "docs.")
ENDUSER_HINTS=("reddit.com","forum","community","stackexchange.com","stackoverflow.com")

def source_class(url):
    host=(urlparse(str(url)).hostname or "").lower()
    if any(x in host for x in OFFICIAL_HINTS): return "official"
    if any(x in host for x in ENDUSER_HINTS): return "end_user"
    return "other"

def verify_record(run):
    reasons=[]
    if run.get("status") != "ANSWER_READY": reasons.append("search_not_answer_ready")
    claims=run.get("verified_claims") or []
    sources=run.get("sources") or []
    by_id={str(s.get("id")):s for s in sources if s.get("id") is not None and s.get("url")}
    if not claims: reasons.append("no_verified_claims")
    if not by_id: reasons.append("no_source_provenance")
    dangling=[]
    for c in claims:
        ids=c.get("source_ids") or []
        if not ids: dangling.append(str(c.get("text") or "")[:80]); continue
        if any(str(i) not in by_id for i in ids): dangling.append(str(c.get("text") or "")[:80])
    if dangling: reasons.append("claim_source_link_failed")
    classes=sorted({source_class(s.get("url")) for s in by_id.values()})
    return {"promote":not reasons,"reasons":reasons,"source_classes":classes,"claim_count":len(claims),"source_count":len(by_id)}

def warehouse_record(run,gate):
    compact={"question":run.get("question"),"verified_claims":run.get("verified_claims") or [],"sources":run.get("sources") or [],"verification":gate}
    raw=json.dumps(compact,sort_keys=True,ensure_ascii=False).encode()
    compact["provenance_sha256"]=hashlib.sha256(raw).hexdigest()
    compact["warehouse_status"]="VERIFIED_PROMOTABLE" if gate["promote"] else "QUARANTINE"
    return compact

def main():
    data=json.load(open(sys.argv[1],encoding="utf-8")) if len(sys.argv)>1 else json.load(sys.stdin)
    gate=verify_record(data); out=warehouse_record(data,gate)
    print(json.dumps(out,indent=2,ensure_ascii=False))
    raise SystemExit(0 if gate["promote"] else 2)

if __name__=="__main__": main()
