#!/usr/bin/env python3
import base64, csv, hashlib, json, re, subprocess, time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO="brianstephanderson-code/anderson-house-test1"
RUN_SECONDS=6180          # 103 minutes; safely below mailbox 2-hour timeout
HEARTBEAT_SECONDS=300     # 5 minutes
PACKET_SIZES=(1,5,10,25,50,100)
OUT=Path(r"C:\AH\OUT\classicquill_granularity_lab.csv")

def gh_json(*args):
    p=subprocess.run(["gh",*args],text=True,capture_output=True,check=True,timeout=60)
    return json.loads(p.stdout)

def load_corpus():
    tree=gh_json("api",f"repos/{REPO}/git/trees/main?recursive=1")["tree"]
    policy=[x for x in tree if x.get("type")=="blob" and x["path"].startswith("hive/") and x["path"].endswith(".md")]
    lines=[]
    for item in policy:
        blob=gh_json("api",f"repos/{REPO}/git/blobs/{item['sha']}")
        text=base64.b64decode(blob["content"]).decode("utf-8","replace")
        lines.extend(text.splitlines())
    return lines

def process_packet(packet):
    rules=0
    unknown=0
    h=hashlib.sha256()
    for line in packet:
        b=line.encode("utf-8","replace")
        h.update(b)
        u=line.upper()
        if any(k in u for k in ("MUST","NEVER","ONLY","REQUIRED","ALWAYS","DO NOT","SHALL")):
            rules+=1
        if "UNKNOWN" in u:
            unknown+=1
    return rules,unknown,h.digest()

def benchmark(lines, packet_size):
    started=time.perf_counter()
    atoms=0
    packets=0
    rules=0
    unknown=0
    for i in range(0,len(lines),packet_size):
        packet=lines[i:i+packet_size]
        r,u,_=process_packet(packet)
        rules+=r; unknown+=u
        atoms+=len(packet); packets+=1
    elapsed=max(time.perf_counter()-started,1e-9)
    return atoms,packets,rules,unknown,elapsed

def publish_lab_heartbeat(started, round_no, packet_size, atoms_total):
    elapsed=int(time.time()-started)
    pct=min(100.0, elapsed/RUN_SECONDS*100.0)
    eta=max(RUN_SECONDS-elapsed,0)
    stamp=datetime.now(timezone.utc).isoformat()
    content=(
        "WORKER=CLASSICQUILL\nSTATUS=ALIVE\nSTATE=BUSY\n"
        "FUNCTION=function_pack_granularity_lab\n"
        f"LAB_ROUND={round_no}\nPACKET_SIZE={packet_size}\n"
        f"ATOMS_IN_CORPUS={atoms_total}\n"
        f"ELAPSED_SECONDS={elapsed}\nETA_SECONDS={eta}\n"
        f"PROGRESS_PCT={pct:.1f}\nUTC={stamp}\n"
    )
    encoded=base64.b64encode(content.encode()).decode()
    path="hive/heartbeat/classicquill.txt"
    cur=subprocess.run(["gh","api",f"repos/{REPO}/contents/{path}"],text=True,capture_output=True)
    args=["gh","api","--method","PUT",f"repos/{REPO}/contents/{path}",
          "-f",f"message=CLASSICQUILL lab heartbeat {stamp}",
          "-f",f"content={encoded}"]
    if cur.returncode==0:
        try:
            args += ["-f",f"sha={json.loads(cur.stdout)['sha']}"]
        except Exception:
            pass
    subprocess.run(args,text=True,capture_output=True,timeout=60)

def main():
    lines=load_corpus()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    new_file=not OUT.exists()
    fh=OUT.open("a",newline="",encoding="utf-8")
    w=csv.writer(fh)
    if new_file:
        w.writerow(["utc","round","packet_size","atoms","packets","elapsed_s","atoms_per_s","rules","unknown"])
        fh.flush()

    started=time.time()
    next_hb=0
    round_no=0
    measurements=0
    last_packet=0
    while time.time()-started < RUN_SECONDS:
        round_no+=1
        for packet_size in PACKET_SIZES:
            if time.time()-started >= RUN_SECONDS:
                break
            atoms,packets,rules,unknown,elapsed=benchmark(lines,packet_size)
            last_packet=packet_size
            measurements+=1
            w.writerow([
                datetime.now(timezone.utc).isoformat(),round_no,packet_size,atoms,packets,
                f"{elapsed:.6f}",f"{atoms/elapsed:.2f}",rules,unknown
            ])
            fh.flush()
            now=time.time()
            if now >= next_hb:
                publish_lab_heartbeat(started,round_no,packet_size,len(lines))
                next_hb=now+HEARTBEAT_SECONDS
        time.sleep(2)

    publish_lab_heartbeat(started,round_no,last_packet,len(lines))
    fh.close()
    print("# CLASSICQUILL GRANULARITY LAB")
    print(f"STATUS=DONE")
    print(f"DURATION_SECONDS={int(time.time()-started)}")
    print(f"ROUNDS={round_no}")
    print(f"MEASUREMENTS={measurements}")
    print(f"ATOMS_IN_CORPUS={len(lines)}")
    print(f"PACKET_SIZES={','.join(map(str,PACKET_SIZES))}")
    print(f"REPORT={OUT}")

if __name__=="__main__":
    main()
