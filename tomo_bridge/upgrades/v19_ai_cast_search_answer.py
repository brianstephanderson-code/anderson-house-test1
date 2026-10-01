#!/data/data/com.termux/files/usr/bin/python
# V19 AI PLANS -> FREE SEARCH -> AI ANSWERS
# Uses curl for transport because it is already proven on this phone.
# Flow:
#   question -> Cloudflare AI cast planner -> free public search -> text fetch
#   -> Cloudflare AI answer brain
#
# No Gemini billing. No paid Google grounding.

import sys, json, subprocess, urllib.parse

ENDPOINT="https://ah-word-count.brian-steph-anderson.workers.dev"

def curl_get(params, timeout=90):
    cmd=["curl","--fail","--silent","--show-error","--get"]
    for k,v in params.items():
        cmd += ["--data-urlencode", f"{k}={v}"]
    cmd += ["--max-time",str(timeout),ENDPOINT]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or "curl failed").strip())
    return json.loads(p.stdout)

def curl_post(payload, timeout=90):
    p=subprocess.run(
        [
            "curl","--fail","--silent","--show-error",
            "--max-time",str(timeout),
            "-H","content-type: application/json",
            "-X","POST",
            "--data-binary","@-",
            ENDPOINT
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or "curl failed").strip())
    return json.loads(p.stdout)

def unique_by_url(rows):
    out=[]
    seen=set()
    for x in rows:
        u=str(x.get("url") or "").strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(x)
    return out

def main():
    q=" ".join(sys.argv[1:]).strip() or input("Question: ").strip()

    print("[AMIGOS] AI UNDERSTANDS QUESTION + BUILDS CASTS...",file=sys.stderr)
    plan=curl_get({
        "type":"CLOUDFLARE_AI_CASTS",
        "query":q
    })

    casts=plan.get("casts") or []
    if not casts:
        print(json.dumps({
            "status":"CAST_ERROR",
            "question":q,
            "planner":plan
        },indent=2))
        raise SystemExit(1)

    print("[AMIGOS] CASTS:",file=sys.stderr)
    for i,c in enumerate(casts,1):
        print(f"  {i}. {c}",file=sys.stderr)

    candidates=[]
    for c in casts[:5]:
        try:
            s=curl_get({
                "type":"SEARCH_WEB_PUBLIC",
                "query":c,
                "limit":"5"
            },60)
            for r in s.get("results",[]) or []:
                r=dict(r)
                r["cast"]=c
                candidates.append(r)
        except Exception as e:
            print(f"[AMIGOS] cast failed softly: {c} :: {e}",file=sys.stderr)

    candidates=unique_by_url(candidates)
    print(f"[AMIGOS] {len(candidates)} UNIQUE SEARCH RESULTS",file=sys.stderr)

    evidence=[]
    for r in candidates[:8]:
        try:
            f=curl_get({
                "type":"FETCH_TEXT",
                "url":r["url"],
                "max_chars":"3500"
            },60)
            text=str(f.get("text") or "").strip()
            if len(text) < 120:
                continue
            evidence.append({
                "title":r.get("title") or "",
                "url":r.get("url") or "",
                "text":text[:3500],
                "source_door":r.get("source_door") or "",
                "cast":r.get("cast") or ""
            })
            if len(evidence) >= 6:
                break
        except Exception:
            continue

    print(f"[AMIGOS] {len(evidence)} READABLE SOURCES",file=sys.stderr)

    if not evidence:
        print(json.dumps({
            "status":"NO_EVIDENCE",
            "question":q,
            "casts":casts,
            "candidate_count":len(candidates)
        },indent=2))
        raise SystemExit(1)

    print("[AMIGOS] AI WRITES ANSWER FROM HARVESTED SOURCES...",file=sys.stderr)
    ans=curl_post({
        "type":"CLOUDFLARE_AI_ANSWER",
        "query":q,
        "evidence":[
            {"title":e["title"],"url":e["url"],"text":e["text"]}
            for e in evidence
        ]
    },90)

    out={
        "status":"ANSWER_READY" if ans.get("ok") else "AI_ERROR",
        "question":q,
        "architecture":"AI CAST PLANNER -> FREE SEARCH -> SOURCE READ -> AI ANSWER",
        "planner_model":plan.get("model"),
        "interpreted_need":plan.get("interpreted_need"),
        "casts":casts,
        "candidate_count":len(candidates),
        "evidence_count":len(evidence),
        "sources":[
            {"title":e["title"],"url":e["url"],"door":e["source_door"],"cast":e["cast"]}
            for e in evidence
        ],
        "answer_model":ans.get("model"),
        "answer":ans.get("answer",""),
        "answer_error":None if ans.get("ok") else ans
    }
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
