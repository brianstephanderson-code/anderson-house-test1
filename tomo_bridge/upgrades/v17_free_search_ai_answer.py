#!/data/data/com.termux/files/usr/bin/python
# V17 FREE SEARCH -> AI ANSWER
# Existing 3 Amigos free web-search door harvests evidence.
# Gemini 3.5 Flash-Lite reads that evidence and writes the answer.
# No Google Search grounding tool is used, so this path does not invoke paid grounding.

import os, sys, json, time, urllib.request, urllib.parse, urllib.error

SEARCH_ENDPOINT = os.environ.get(
    "AMIGOS_SEARCH_ENDPOINT",
    "https://ah-word-count.brian-steph-anderson.workers.dev"
)
MODEL = os.environ.get("AMIGOS_GEMINI_MODEL", "gemini-3.5-flash-lite")

SYSTEM = """You are the answer brain for The 3 Amigos.
You receive a user's question plus evidence harvested by the Amigos' own web-search system.
Answer the exact question directly and practically.
Use only the supplied evidence for web-derived factual claims.
Preserve the user's hard boundaries.
Do not invent facts, routes, dates, places, products, or source details.
If the evidence is insufficient, say exactly what is missing.
When useful, distinguish official/provider evidence from end-user/practitioner evidence.
Cite supplied sources inline as [1], [2], etc.
Finish with a short Sources section listing the cited source numbers and URLs.
Do not expose hidden chain-of-thought.
"""

def fetch_search(question):
    params = {
        "type": "SEARCH_END_TO_END_V1",
        "query": question,
        "limit": "10",
        "read_limit": "6",
        "max_chars": "3500",
        "browser_fallback": "1",
    }
    url = SEARCH_ENDPOINT + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":"3-Amigos-V17/1.0"})
    started = time.time()
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data, round(time.time()-started,1)

def evidence_bundle(search):
    rows=[]
    for i,e in enumerate(search.get("evidence",[]) or [], start=1):
        text=(e.get("text") or "").strip()
        if not text:
            continue
        rows.append({
            "n": i,
            "title": e.get("title") or "",
            "url": e.get("url") or "",
            "source_door": e.get("source_door") or "",
            "semantic_relevance": e.get("semantic_relevance"),
            "text": text[:3500],
        })
    return rows

def ask_gemini(question, evidence):
    key=os.environ.get("GEMINI_API_KEY","").strip()
    if not key:
        return {"status":"SETUP_NEEDED","reason":"GEMINI_API_KEY is not set"}

    if not evidence:
        return {"status":"NO_EVIDENCE","reason":"Amigos search returned no readable evidence"}

    evidence_text="\n\n".join(
        f"[{e['n']}] {e['title']}\nURL: {e['url']}\nDOOR: {e['source_door']}\nTEXT:\n{e['text']}"
        for e in evidence
    )

    prompt=f"""USER QUESTION:
{question}

AMIGOS HARVESTED EVIDENCE:
{evidence_text}

Write the best supported answer now. If the evidence does not fully answer the question, give the supported part and clearly state the gap."""

    endpoint=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    payload={
        "system_instruction":{"parts":[{"text":SYSTEM}]},
        "contents":[{"role":"user","parts":[{"text":prompt}]}],
        "generationConfig":{"temperature":0.2}
    }

    req=urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type":"application/json","x-goog-api-key":key},
        method="POST"
    )

    started=time.time()
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            obj=json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body=e.read().decode("utf-8","replace")
        return {"status":"AI_HTTP_ERROR","code":e.code,"body":body[:4000],"model":MODEL}
    except Exception as e:
        return {"status":"AI_ERROR","error":repr(e),"model":MODEL}

    texts=[]
    for c in obj.get("candidates",[]) or []:
        for p in (c.get("content",{}) or {}).get("parts",[]) or []:
            if p.get("text"):
                texts.append(p["text"])

    return {
        "status":"ANSWER_READY" if texts else "NO_ANSWER",
        "model":MODEL,
        "seconds":round(time.time()-started,1),
        "answer":"\n".join(texts).strip()
    }

def main():
    q=" ".join(sys.argv[1:]).strip()
    if not q:
        q=input("Question: ").strip()

    print("[AMIGOS] CASTING FREE WEB NET...", file=sys.stderr)
    try:
        search, search_seconds=fetch_search(q)
    except Exception as e:
        print(json.dumps({
            "status":"SEARCH_ERROR",
            "question":q,
            "error":repr(e)
        },indent=2))
        raise SystemExit(1)

    evidence=evidence_bundle(search)
    print(f"[AMIGOS] HARVESTED {len(evidence)} READABLE SOURCES IN {search_seconds}s", file=sys.stderr)
    print("[AMIGOS] HANDING EVIDENCE TO AI BRAIN...", file=sys.stderr)

    ai=ask_gemini(q,evidence)

    out={
        "status":ai.get("status"),
        "question":q,
        "architecture":"FREE AMIGOS SEARCH -> GEMINI ANSWER BRAIN",
        "search_seconds":search_seconds,
        "search_ok":search.get("ok"),
        "search_sufficiency":search.get("sufficiency"),
        "candidate_count":search.get("candidate_count"),
        "shortlist_count":search.get("shortlist_count"),
        "evidence_count":len(evidence),
        "sources":[{"n":e["n"],"title":e["title"],"url":e["url"],"door":e["source_door"]} for e in evidence],
        "model":ai.get("model",MODEL),
        "ai_seconds":ai.get("seconds"),
        "answer":ai.get("answer",""),
    }
    if ai.get("status")!="ANSWER_READY":
        out["ai_error"]={k:v for k,v in ai.items() if k not in ("answer",)}

    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
