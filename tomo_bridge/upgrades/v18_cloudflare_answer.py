#!/data/data/com.termux/files/usr/bin/python
# V18 FREE SEARCH -> CLOUDFLARE AI ANSWER
import sys,json,time,urllib.request,urllib.parse

ENDPOINT="https://ah-word-count.brian-steph-anderson.workers.dev"

def get_search(q):
    params={"type":"SEARCH_END_TO_END_V1","query":q,"limit":"10","read_limit":"6","max_chars":"3500","browser_fallback":"1"}
    url=ENDPOINT+"?"+urllib.parse.urlencode(params)
    t=time.time()
    with urllib.request.urlopen(url,timeout=90) as r:
        data=json.loads(r.read().decode())
    return data,round(time.time()-t,1)

def call_answer(q,evidence):
    payload={
      "type":"CLOUDFLARE_AI_ANSWER",
      "query":q,
      "evidence":[
        {
          "title":e.get("title",""),
          "url":e.get("url",""),
          "text":(e.get("text") or "")[:3000]
        }
        for e in (evidence or [])[:6]
      ]
    }
    req=urllib.request.Request(
      ENDPOINT,
      data=json.dumps(payload).encode(),
      headers={"content-type":"application/json"},
      method="POST"
    )
    t=time.time()
    with urllib.request.urlopen(req,timeout=90) as r:
      data=json.loads(r.read().decode())
    return data,round(time.time()-t,1)

def main():
    q=" ".join(sys.argv[1:]).strip() or input("Question: ").strip()
    print("[AMIGOS] FREE SEARCH...",file=sys.stderr)
    s,ss=get_search(q)
    ev=s.get("evidence",[]) or []
    print(f"[AMIGOS] {len(ev)} EVIDENCE ITEMS IN {ss}s",file=sys.stderr)
    print("[AMIGOS] CLOUDFLARE AI ANSWER BRAIN...",file=sys.stderr)
    a,ats=call_answer(q,ev)
    out={
      "status":"ANSWER_READY" if a.get("ok") else "AI_ERROR",
      "question":q,
      "architecture":"FREE AMIGOS SEARCH -> CLOUDFLARE WORKERS AI",
      "search_seconds":ss,
      "ai_seconds":ats,
      "evidence_count":len(ev),
      "model":a.get("model"),
      "answer":a.get("answer",""),
      "ai_error":None if a.get("ok") else a
    }
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
