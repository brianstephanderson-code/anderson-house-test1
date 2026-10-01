#!/data/data/com.termux/files/usr/bin/python
# V20 EVIDENCE-FENCED AI SEARCH
# question -> constrained AI casts -> free search -> source read -> relevance gate
# -> evidence-bound draft -> second-pass claim verification -> final answer

import sys,json,subprocess

ENDPOINT="https://ah-word-count.brian-steph-anderson.workers.dev"

def curl_get(params,timeout=90):
    cmd=["curl","--fail","--silent","--show-error","--get"]
    for k,v in params.items():
        cmd += ["--data-urlencode",f"{k}={v}"]
    cmd += ["--max-time",str(timeout),ENDPOINT]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        raise RuntimeError((p.stderr or p.stdout or "curl failed").strip())
    return json.loads(p.stdout)

def curl_post(payload,timeout=120):
    p=subprocess.run(
        ["curl","--fail","--silent","--show-error","--max-time",str(timeout),
         "-H","content-type: application/json","-X","POST","--data-binary","@-",ENDPOINT],
        input=json.dumps(payload),
        capture_output=True,text=True
    )
    if p.returncode!=0:
        raise RuntimeError((p.stderr or p.stdout or "curl failed").strip())
    return json.loads(p.stdout)

def unique_by_url(rows):
    out=[]; seen=set()
    for x in rows:
        u=str(x.get("url") or "").strip()
        if not u or u in seen: continue
        seen.add(u); out.append(x)
    return out

def rank_candidates(rows, question):
    q=str(question or "").lower()
    route_terms=("walk","walking","route","path","trail","towpath","canal","hike","hiking")
    endpoints=[]
    if " from " in q and " to " in q:
        try:
            after=q.split(" from ",1)[1]
            a,b=after.split(" to ",1)
            b=b.split(" in ",1)[0].split(" during ",1)[0].split(" for ",1)[0]
            endpoints=[a.strip(),b.strip()]
        except Exception:
            endpoints=[]
    def score(r):
        title=str(r.get("title") or "").lower()
        snippet=str(r.get("snippet") or "").lower()
        blob=title+" "+snippet
        s=0
        if any(t in blob for t in route_terms): s+=6
        for ep in endpoints:
            toks=[w for w in ep.replace(","," ").split() if len(w)>=4]
            if toks and any(w in blob for w in toks): s+=5
        if "edinburgh" in blob and "glasgow" in blob: s+=10
        if "walk" in title or "walking" in title or "canal" in title or "towpath" in title: s+=4
        return s
    return sorted(rows,key=score,reverse=True)

def render_verified(ans):
    direct=str(ans.get("direct_answer") or "").strip()
    claims=ans.get("claims") or []
    uncertainty=str(ans.get("uncertainty") or "").strip()
    sources=ans.get("sources") or []

    lines=[]
    if direct: lines.append(direct)
    for c in claims:
        text=str(c.get("text") or "").strip()
        ids=c.get("source_ids") or []
        cites=" ".join(f"[{i}]" for i in ids)
        if text and text!=direct:
            lines.append(f"{text} {cites}".strip())
    if uncertainty:
        lines.append("Uncertainty: "+uncertainty)
    if sources:
        lines.append("Sources:")
        for s in sources:
            lines.append(f"[{s.get('id')}] {s.get('title') or ''} — {s.get('url') or ''}")
    return "\n\n".join(lines)

def main():
    q=" ".join(sys.argv[1:]).strip() or input("Question: ").strip()

    print("[AMIGOS] 1/6 AI UNDERSTANDS QUESTION...",file=sys.stderr)
    plan=curl_get({"type":"CLOUDFLARE_AI_CASTS_V20","query":q})

    casts=plan.get("casts") or []
    if not casts:
        print(json.dumps({"status":"CAST_ERROR","question":q,"planner":plan},indent=2))
        raise SystemExit(1)

    print("[AMIGOS] HARD CONSTRAINTS:",plan.get("hard_constraints"),file=sys.stderr)
    print("[AMIGOS] UNKNOWN:",plan.get("unknown"),file=sys.stderr)
    print("[AMIGOS] 2/6 SEARCH CASTS:",file=sys.stderr)
    for i,c in enumerate(casts,1):
        print(f"  {i}. {c}",file=sys.stderr)

    candidates=[]
    for c in casts[:6]:
        try:
            s=curl_get({"type":"SEARCH_WEB_PUBLIC","query":c,"limit":"6"},60)
            for r in s.get("results",[]) or []:
                rr=dict(r); rr["cast"]=c; candidates.append(rr)
        except Exception as e:
            print(f"[AMIGOS] soft search fail: {c} :: {e}",file=sys.stderr)

    candidates=rank_candidates(unique_by_url(candidates),q)
    print(f"[AMIGOS] 3/6 {len(candidates)} UNIQUE RESULTS",file=sys.stderr)

    evidence=[]
    for r in candidates[:16]:
        try:
            f=curl_get({"type":"FETCH_TEXT","url":r["url"],"max_chars":"4000"},60)
            text=str(f.get("text") or "").strip()
            if len(text)<150: continue
            evidence.append({
                "title":r.get("title") or "",
                "url":r.get("url") or "",
                "text":text[:4000],
                "source_door":r.get("source_door") or "",
                "cast":r.get("cast") or ""
            })
            if len(evidence)>=8: break
        except Exception:
            continue

    print(f"[AMIGOS] 4/6 {len(evidence)} READABLE SOURCES",file=sys.stderr)
    if not evidence:
        print(json.dumps({
            "status":"NO_EVIDENCE","question":q,"casts":casts,
            "candidate_count":len(candidates)
        },indent=2))
        raise SystemExit(1)

    print("[AMIGOS] 5/6 RELEVANCE + SOURCE-PROOF + CLAIM-CHECK...",file=sys.stderr)
    ans=curl_post({
        "type":"CLOUDFLARE_EVIDENCE_ANSWER",
        "query":q,
        "evidence":[{"title":e["title"],"url":e["url"],"text":e["text"]} for e in evidence]
    },120)

    status="ANSWER_READY" if ans.get("ok") else "HOLD_NEEDS_RECAST"
    final_text=render_verified(ans) if ans.get("ok") else ""

    print("[AMIGOS] 6/6 "+status,file=sys.stderr)

    out={
        "status":status,
        "question":q,
        "architecture":"AI UNDERSTAND -> CONSTRAINED CASTS -> FREE SEARCH -> READ -> RELEVANCE -> EVIDENCE ANSWER -> CLAIM VERIFY",
        "planner_model":plan.get("model"),
        "interpreted_need":plan.get("interpreted_need"),
        "hard_constraints":plan.get("hard_constraints"),
        "unknown":plan.get("unknown"),
        "casts":casts,
        "candidate_count":len(candidates),
        "readable_evidence_count":len(evidence),
        "answer_model":ans.get("model"),
        "relevance":ans.get("relevance"),
        "verified_claims":ans.get("claims") or [],
        "rejected_claims":ans.get("rejected_claims") or [],
        "sources":ans.get("sources") or [],
        "final_answer":final_text,
        "error":None if ans.get("ok") else ans
    }
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
