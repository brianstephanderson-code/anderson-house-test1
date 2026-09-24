#!/usr/bin/env python3
import base64, hashlib, json, os, re, subprocess, time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

REPO="brianstephanderson-code/anderson-house-test1"
WORKERS=4
RUN_SECONDS=3600
HEARTBEAT_SECONDS=300
OUT=Path(r"C:\AH\OUT\classicquill_fourcore_lab.txt")

def gh_json(*args):
    p=subprocess.run(["gh",*args],text=True,capture_output=True,check=True,timeout=60)
    return json.loads(p.stdout)

def load_docs():
    tree=gh_json("api",f"repos/{REPO}/git/trees/main?recursive=1")["tree"]
    items=[x for x in tree if x.get("type")=="blob" and x["path"].startswith("hive/") and x["path"].endswith(".md")]
    docs=[]
    for item in items:
        blob=gh_json("api",f"repos/{REPO}/git/blobs/{item['sha']}")
        text=base64.b64decode(blob["content"]).decode("utf-8","replace")
        docs.append((item["path"],text))
    return docs

def lane(task):
    lane_id, docs, rounds = task
    hard=unknown=headings=todos=0
    digest=hashlib.sha256()
    for _ in range(rounds):
        for path,text in docs:
            digest.update(path.encode())
            digest.update(text.encode("utf-8","replace"))
            lines=text.splitlines()
            hard += sum(1 for line in lines if re.search(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b",line,re.I))
            unknown += sum(1 for line in lines if re.search(r"\bUNKNOWN\b",line,re.I))
            headings += sum(1 for line in lines if re.match(r"^#{1,6}\s+",line))
            todos += sum(1 for line in lines if re.search(r"\b(TODO|TBD|FIXME)\b|\?\?\?",line,re.I))
    return lane_id,hard,unknown,headings,todos,digest.hexdigest()

def publish(started, batches, state="BUSY"):
    elapsed=int(time.time()-started)
    eta=max(RUN_SECONDS-elapsed,0) if state=="BUSY" else 0
    pct=min(100.0,elapsed/RUN_SECONDS*100.0)
    stamp=datetime.now(timezone.utc).isoformat()
    content=(
        "WORKER=CLASSICQUILL\nSTATUS=ALIVE\n"
        f"STATE={state}\nFUNCTION=fourcore_granularity_lab\n"
        f"WORKERS={WORKERS}\nBATCHES_COMPLETED={batches}\n"
        f"ELAPSED_SECONDS={elapsed}\nETA_SECONDS={eta}\nPROGRESS_PCT={pct:.1f}\nUTC={stamp}\n"
    )
    encoded=base64.b64encode(content.encode()).decode()
    path="hive/heartbeat/classicquill.txt"
    cur=subprocess.run(["gh","api",f"repos/{REPO}/contents/{path}"],text=True,capture_output=True)
    args=["gh","api","--method","PUT",f"repos/{REPO}/contents/{path}",
          "-f",f"message=CLASSICQUILL 4-core heartbeat {stamp}",
          "-f",f"content={encoded}"]
    if cur.returncode==0:
        try: args += ["-f",f"sha={json.loads(cur.stdout)['sha']}"]
        except Exception: pass
    subprocess.run(args,text=True,capture_output=True,timeout=60)

def main():
    docs=load_docs()
    started=time.time()
    next_hb=0
    batches=0
    totals=[0,0,0,0]
    last_hashes=[]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        while time.time()-started < RUN_SECONDS:
            tasks=[(i,docs,25) for i in range(WORKERS)]
            results=list(pool.map(lane,tasks))
            batches+=1
            for _,h,u,hd,t,d in results:
                totals[0]+=h; totals[1]+=u; totals[2]+=hd; totals[3]+=t
                last_hashes.append(d)
            if time.time() >= next_hb:
                publish(started,batches)
                next_hb=time.time()+HEARTBEAT_SECONDS
    publish(started,batches,state="DONE")
    report=(
        "# CLASSICQUILL FOUR-CORE LAB\n"
        f"WORKERS={WORKERS}\n"
        f"DURATION_SECONDS={int(time.time()-started)}\n"
        f"BATCHES={batches}\n"
        f"HARD_RULE_HITS={totals[0]}\nUNKNOWN_HITS={totals[1]}\n"
        f"HEADING_HITS={totals[2]}\nTODO_HITS={totals[3]}\n"
        f"HASH_SAMPLES={len(last_hashes)}\n"
    )
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(report,encoding="utf-8")
    print(report,end="")

if __name__=="__main__":
    main()
