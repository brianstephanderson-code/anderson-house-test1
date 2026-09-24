#!/usr/bin/env python3
import base64, hashlib, json, re, subprocess, time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

REPO="brianstephanderson-code/anderson-house-test1"
WORKERS=4
AH=Path(r"C:\AH")
CHECKPOINTS=AH/"WORK"/"checkpoints"
OUT=AH/"OUT"/"classicquill_hive_latest.txt"
LINES_PER_ATOM=40
ATOMS_PER_PACKET=8
MAX_RETRIES=2

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

def shred(docs):
    atoms=[]; atom_id=0
    for path,text in docs:
        lines=text.splitlines()
        for start in range(0,len(lines),LINES_PER_ATOM):
            atom_id+=1
            atoms.append({"id":atom_id,"source":path,"start_line":start+1,"text":"\n".join(lines[start:start+LINES_PER_ATOM])})
    return atoms

def atom_work(atom):
    text=atom["text"]; lines=text.splitlines()
    return {
        "id":atom["id"],"source":atom["source"],"start_line":atom["start_line"],"lines":len(lines),
        "hard_rules":sum(1 for line in lines if re.search(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b",line,re.I)),
        "unknown":sum(1 for line in lines if re.search(r"\bUNKNOWN\b",line,re.I)),
        "headings":sum(1 for line in lines if re.match(r"^#{1,6}\s+",line)),
        "todos":sum(1 for line in lines if re.search(r"\b(TODO|TBD|FIXME)\b|\?\?\?",line,re.I)),
        "sha256":hashlib.sha256(text.encode("utf-8","replace")).hexdigest()
    }

def packet_work(packet):
    return [atom_work(a) for a in packet]

def check_packet(packet,result):
    if not isinstance(result,list) or len(result)!=len(packet):
        return False,"count_mismatch"
    expected={a["id"]:a for a in packet}; seen=set()
    for row in result:
        aid=row.get("id")
        if aid not in expected or aid in seen: return False,"identity_mismatch"
        seen.add(aid); atom=expected[aid]
        digest=hashlib.sha256(atom["text"].encode("utf-8","replace")).hexdigest()
        if row.get("sha256")!=digest: return False,f"hash_mismatch_{aid}"
        if row.get("lines")!=len(atom["text"].splitlines()): return False,f"line_count_mismatch_{aid}"
    return True,"VERIFIED"

def cp_path():
    CHECKPOINTS.mkdir(parents=True,exist_ok=True)
    return CHECKPOINTS/"classicquill-hive.json"

def load_cp():
    try: return json.loads(cp_path().read_text(encoding="utf-8"))
    except Exception: return {}

def save_cp(data):
    p=cp_path(); tmp=p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,sort_keys=True,indent=2),encoding="utf-8"); tmp.replace(p)

def publish(phase,packet_current,packet_total,verified_atoms,retries,started,state="BUSY"):
    elapsed=max(int(time.time()-started),0)
    pct=(100.0*packet_current/packet_total) if packet_total else 100.0
    avg=(elapsed//packet_current) if packet_current else 0
    eta=avg*max(packet_total-packet_current,0)
    stamp=datetime.now(timezone.utc).isoformat()
    content=(
        "WORKER=CLASSICQUILL\nSTATUS=ALIVE\n"
        f"STATE={state}\nFUNCTION=hive_campaign\nPHASE={phase}\nWORKERS_ACTIVE={WORKERS if state=='BUSY' else 0}\n"
        f"ATOM_CURRENT={verified_atoms}\nPACKET_CURRENT={packet_current}\nPACKET_TOTAL={packet_total}\n"
        f"VERIFIED_ATOMS={verified_atoms}\nRETRY_COUNT={retries}\nCHECKPOINT_PACKET={packet_current}\n"
        f"PROGRESS_PCT={pct:.1f}\nELAPSED_SECONDS={elapsed}\nAVG_PACKET_SECONDS={avg}\nETA_SECONDS={eta}\nUTC={stamp}\n"
    )
    enc=base64.b64encode(content.encode()).decode(); path="hive/heartbeat/classicquill.txt"
    cur=subprocess.run(["gh","api",f"repos/{REPO}/contents/{path}"],text=True,capture_output=True)
    args=["gh","api","--method","PUT",f"repos/{REPO}/contents/{path}","-f",f"message=CLASSICQUILL hive heartbeat {stamp}","-f",f"content={enc}"]
    if cur.returncode==0:
        try: args+=["-f",f"sha={json.loads(cur.stdout)['sha']}"]
        except Exception: pass
    subprocess.run(args,text=True,capture_output=True,timeout=60)

def main():
    started=time.time(); docs=load_docs(); atoms=shred(docs)
    packets=[atoms[i:i+ATOMS_PER_PACKET] for i in range(0,len(atoms),ATOMS_PER_PACKET)]
    total=len(packets); cp=load_cp()
    next_packet=min(int(cp.get("next_packet",0) or 0),total)
    verified=int(cp.get("verified_atoms",0) or 0); retries=int(cp.get("retries",0) or 0)
    publish("SHREDDED",next_packet,total,verified,retries,started)
    totals={"hard_rules":0,"unknown":0,"headings":0,"todos":0}
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        idx=next_packet
        while idx<total:
            wave_idx=list(range(idx,min(idx+WORKERS,total)))
            wave=[packets[i] for i in wave_idx]
            futures=[pool.submit(packet_work,p) for p in wave]
            for pi,pkt,fut in zip(wave_idx,wave,futures):
                attempt=0
                while True:
                    try:
                        result=fut.result(); ok,reason=check_packet(pkt,result)
                    except Exception as exc:
                        ok,reason=False,f"worker_exception:{exc}"
                    if ok:
                        for row in result:
                            for k in totals: totals[k]+=row[k]
                        verified+=len(pkt); completed=pi+1
                        save_cp({"next_packet":completed,"verified_atoms":verified,"retries":retries,"total_packets":total,"total_atoms":len(atoms),"updated_utc":datetime.now(timezone.utc).isoformat()})
                        publish("CHECKPOINT",completed,total,verified,retries,started)
                        break
                    attempt+=1; retries+=1; publish("RETRY",pi,total,verified,retries,started)
                    if attempt>MAX_RETRIES: raise RuntimeError(f"packet {pi+1} failed checker: {reason}")
                    result=packet_work(pkt)
                    class Done:
                        def result(self): return result
                    fut=Done()
            idx=wave_idx[-1]+1
    publish("VERIFIED_DONE",total,total,len(atoms),retries,started,state="DONE")
    report=(f"VERIFIED_DONE atoms={len(atoms)} packets={total} retries={retries} "
            f"hard_rules={totals['hard_rules']} unknown={totals['unknown']} headings={totals['headings']} todos={totals['todos']} "
            f"checkpoint={cp_path()}")
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(report+"\n",encoding="utf-8")
    print(report)

if __name__=="__main__":
    main()
