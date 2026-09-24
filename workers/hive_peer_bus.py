#!/usr/bin/env python3
import base64, hashlib, json, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

REPO = "brianstephanderson-code/anderson-house-test1"
BUS_MESSAGES = "hive/bus/messages"
BUS_ACKS = "hive/bus/acks"

def _run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check, timeout=60)

def _parse(text):
    out={}
    for raw in text.splitlines():
        line=raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k,v=line.split("=",1); out[k.strip()]=v.strip()
    return out

def _reply_status(msg, worker):
    typ=msg.get("TYPE","").upper()
    payload=msg.get("PAYLOAD","")
    if typ=="PING":
        return "PONG", f"pong_from={worker}"
    if typ=="STATUS_REQUEST":
        return "STATUS", f"alive={worker}"
    if typ=="VERIFY_REQUEST":
        digest=hashlib.sha256(payload.encode("utf-8","replace")).hexdigest()
        return "VERIFIED", f"sha256={digest}"
    if typ=="HANDOFF_REQUEST":
        return "ACCEPTED", f"handoff_ready={worker}"
    if typ=="ACK":
        return "ACK_RECEIVED", "ack_not_replied"
    return "UNSUPPORTED", f"type={typ or 'UNKNOWN'}"

def _ack_text(msg, worker):
    status, detail=_reply_status(msg,worker)
    stamp=datetime.now(timezone.utc).isoformat()
    return (
        f"MESSAGE_ID={msg.get('MESSAGE_ID','')}\n"
        f"FROM={worker}\nTO={msg.get('FROM','')}\n"
        f"TYPE=ACK\nSTATUS={status}\nDETAIL={detail}\n"
        f"CORRELATION_ID={msg.get('MESSAGE_ID','')}\nUTC={stamp}\n"
    )

def _git_push_resilient(root, max_attempts=4):
    last=""
    for attempt in range(1,max_attempts+1):
        p=_run(["git","push","origin","main"],cwd=root,check=False)
        if p.returncode==0:return
        last=(p.stderr or p.stdout or "").strip()
        _run(["git","fetch","origin"],cwd=root)
        r=_run(["git","rebase","origin/main"],cwd=root,check=False)
        if r.returncode!=0:
            _run(["git","rebase","--abort"],cwd=root,check=False)
            raise RuntimeError((r.stderr or r.stdout).strip())
        time.sleep(min(attempt,3))
    raise RuntimeError(last or "push failed")

def process_local(worker, root):
    root=Path(root)
    msgdir=root/BUS_MESSAGES
    ackdir=root/BUS_ACKS
    if not msgdir.exists(): return 0
    ackdir.mkdir(parents=True,exist_ok=True)
    made=0
    for p in sorted(msgdir.glob("*.msg")):
        try: msg=_parse(p.read_text(encoding="utf-8",errors="replace"))
        except Exception: continue
        if msg.get("CHANNEL","").upper() != "CROSSTALK": continue
        if msg.get("CHANNEL","").upper() != "CROSSTALK": continue
        if msg.get("TO") not in {worker,"ALL"}: continue
        mid=msg.get("MESSAGE_ID",p.stem)
        ack=ackdir/f"{mid}.{worker}.ack"
        if ack.exists(): continue
        ack.write_text(_ack_text(msg,worker),encoding="utf-8")
        made+=1
    if made:
        _run(["git","add",BUS_ACKS],cwd=root)
        if _run(["git","diff","--cached","--quiet"],cwd=root,check=False).returncode!=0:
            stamp=datetime.now(timezone.utc).isoformat()
            _run(["git","commit","-m",f"{worker} peer-bus ack {stamp}"],cwd=root)
            _run(["git","pull","--rebase","origin","main"],cwd=root)
            _git_push_resilient(root)
    return made

def _gh(*args, check=True):
    return _run(["gh",*args],check=check)

def process_api(worker, repo=REPO):
    listing=_gh("api",f"repos/{repo}/contents/{BUS_MESSAGES}",check=False)
    if listing.returncode!=0:return 0
    try: items=json.loads(listing.stdout)
    except Exception:return 0
    made=0
    for item in items:
        if item.get("type")!="file" or not item.get("name","").endswith(".msg"): continue
        raw=_gh("api",f"repos/{repo}/contents/{BUS_MESSAGES}/{item['name']}",check=False)
        if raw.returncode!=0: continue
        try:
            obj=json.loads(raw.stdout)
            text=base64.b64decode(obj["content"]).decode("utf-8","replace")
            msg=_parse(text)
        except Exception:
            continue
        if msg.get("TO") not in {worker,"ALL"}: continue
        mid=msg.get("MESSAGE_ID",item["name"][:-4])
        ack_path=f"{BUS_ACKS}/{mid}.{worker}.ack"
        exists=_gh("api",f"repos/{repo}/contents/{ack_path}",check=False)
        if exists.returncode==0: continue
        content=base64.b64encode(_ack_text(msg,worker).encode()).decode()
        stamp=datetime.now(timezone.utc).isoformat()
        put=_gh("api","--method","PUT",f"repos/{repo}/contents/{ack_path}",
                "-f",f"message={worker} peer-bus ack {stamp}",
                "-f",f"content={content}",check=False)
        if put.returncode==0: made+=1
    return made

def process_bus(worker, root=None):
    if root is not None and (Path(root)/".git").exists():
        return process_local(worker,root)
    return process_api(worker)
