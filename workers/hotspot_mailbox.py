#!/usr/bin/env python3
import hashlib, json, re, shutil, subprocess, time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from hive_peer_bus import process_bus

ROOT = Path.home() / "anderson-house-mailbox"
JOBS = ROOT / "jobs"
RESULTS = ROOT / "results"
HEARTBEAT = ROOT / "hive" / "heartbeat" / "hotspot.txt"
CHECKPOINTS = ROOT / "work" / "checkpoints"

WORKER = "HOTSPOT"
INTERVAL = 30
HEARTBEAT_INTERVAL = 300
MAX_WORKERS = 2
_last_heartbeat = 0.0
_busy_job = ""
_phase = ""
_packet_current = 0
_packet_total = 0
_verified_atoms = 0
_retry_count = 0
_job_started = 0.0

def run(*args, check=True):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)

def git_push_resilient(max_attempts=4):
    last=""
    for attempt in range(1,max_attempts+1):
        p=run("git","push","origin","main",check=False)
        if p.returncode==0: return
        last=(p.stderr or p.stdout or "").strip()
        run("git","fetch","origin")
        r=run("git","rebase","origin/main",check=False)
        if r.returncode!=0:
            run("git","rebase","--abort",check=False)
            raise RuntimeError((r.stderr or r.stdout).strip())
        time.sleep(min(attempt,3))
    raise RuntimeError(f"push failed: {last}")

def pull():
    run("git","pull","--rebase","--autostash","origin","main")

def read_text(path,default="NA"):
    try: return Path(path).read_text().strip()
    except Exception: return default

def health():
    cap=read_text("/sys/class/power_supply/battery/capacity")
    charge=read_text("/sys/class/power_supply/battery/status")
    temp="NA"
    for p in ["/sys/class/power_supply/battery/temp","/sys/class/thermal/thermal_zone0/temp"]:
        try:
            raw=float(Path(p).read_text().strip())
            if raw>1000: raw/=1000.0
            elif raw>100: raw/=10.0
            if -20<=raw<=120:
                temp=f"{raw:.1f}"; break
        except Exception: pass
    mem="NA"
    try:
        vals={}
        for line in Path("/proc/meminfo").read_text().splitlines():
            if ":" in line:
                k,v=line.split(":",1); vals[k]=int(v.strip().split()[0])
        total=vals["MemTotal"]; avail=vals.get("MemAvailable",vals.get("MemFree",0))
        mem=f"{100.0*(total-avail)/total:.1f}"
    except Exception: pass
    try:
        _,_,free=shutil.disk_usage(str(Path.home()))
        disk=f"{free/(1024**3):.1f}"
    except Exception: disk="NA"
    return {"BATTERY_PCT":cap,"CHARGE_STATE":charge,"TEMP_C":temp,"MEMORY_PCT":mem,"DISK_FREE_GB":disk}

def publish_heartbeat(force=False):
    global _last_heartbeat
    now=time.time()
    if not force and now-_last_heartbeat<HEARTBEAT_INTERVAL: return
    h=health()
    elapsed=max(int(now-_job_started),0) if _busy_job and _job_started else 0
    pct=(100.0*_packet_current/_packet_total) if _packet_total else 0.0
    eta=0
    if _packet_current>0:
        avg=elapsed/_packet_current
        eta=int(avg*max(_packet_total-_packet_current,0))
    stamp=datetime.now(timezone.utc).isoformat()
    HEARTBEAT.parent.mkdir(parents=True,exist_ok=True)
    HEARTBEAT.write_text(
        f"WORKER={WORKER}\nSTATUS=ALIVE\nSTATE={'BUSY' if _busy_job else 'FREE'}\n"
        f"JOB_ID={_busy_job}\nFUNCTION=hotspot_hive_campaign\nPHASE={_phase}\n"
        f"WORKERS_ACTIVE={MAX_WORKERS if _busy_job else 0}\n"
        f"PACKET_CURRENT={_packet_current}\nPACKET_TOTAL={_packet_total}\n"
        f"VERIFIED_ATOMS={_verified_atoms}\nRETRY_COUNT={_retry_count}\n"
        f"PROGRESS_PCT={pct:.1f}\nELAPSED_SECONDS={elapsed}\nETA_SECONDS={eta}\n"
        f"BATTERY_PCT={h['BATTERY_PCT']}\nCHARGE_STATE={h['CHARGE_STATE']}\n"
        f"MEMORY_PCT={h['MEMORY_PCT']}\nDISK_FREE_GB={h['DISK_FREE_GB']}\n"
        f"TEMP_C={h['TEMP_C']}\nUTC={stamp}\n", encoding="utf-8")
    run("git","add",str(HEARTBEAT.relative_to(ROOT)))
    if run("git","diff","--cached","--quiet",check=False).returncode!=0:
        run("git","commit","-m",f"HOTSPOT heartbeat {stamp}")
        run("git","pull","--rebase","origin","main")
        git_push_resilient()
    _last_heartbeat=now

def parse_job(path):
    d={}
    for raw in path.read_text().splitlines():
        line=raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k,v=line.split("=",1); d[k.strip()]=v.strip()
    return d

def load_docs():
    files=sorted((ROOT/"hive").rglob("*.md")) if (ROOT/"hive").exists() else []
    return [(str(p.relative_to(ROOT)),p.read_text(encoding="utf-8",errors="replace")) for p in files]

def shred():
    atoms=[]; aid=0
    for path,text in load_docs():
        lines=text.splitlines()
        for start in range(0,len(lines),60):
            aid+=1
            atoms.append({"id":aid,"source":path,"text":"\n".join(lines[start:start+60])})
    return atoms

def atom_work(atom):
    text=atom["text"]
    return {"id":atom["id"],"sha256":hashlib.sha256(text.encode("utf-8","replace")).hexdigest(),
            "hard_rules":sum(1 for line in text.splitlines() if re.search(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b",line,re.I))}

def packet_work(packet):
    return [atom_work(a) for a in packet]

def check_packet(packet,result):
    if len(packet)!=len(result): return False
    expected={a["id"]:hashlib.sha256(a["text"].encode("utf-8","replace")).hexdigest() for a in packet}
    return all(r.get("id") in expected and r.get("sha256")==expected[r["id"]] for r in result)

def cp_path(job_id):
    CHECKPOINTS.mkdir(parents=True,exist_ok=True)
    return CHECKPOINTS/f"{job_id}.json"

def run_campaign(job_id):
    global _phase,_packet_current,_packet_total,_verified_atoms,_retry_count
    atoms=shred()
    packets=[atoms[i:i+6] for i in range(0,len(atoms),6)]
    _packet_total=len(packets)
    cp={}
    try: cp=json.loads(cp_path(job_id).read_text())
    except Exception: pass
    start=min(int(cp.get("next_packet",0) or 0),len(packets))
    _verified_atoms=int(cp.get("verified_atoms",0) or 0)
    _retry_count=int(cp.get("retries",0) or 0)
    _packet_current=start
    _phase="SHREDDED"; publish_heartbeat(force=True)
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for i in range(start,len(packets)):
            pkt=packets[i]; attempt=0
            while True:
                _phase="WORK"
                try:
                    result=pool.submit(packet_work,pkt).result()
                    _phase="CHECK"
                    ok=check_packet(pkt,result)
                except Exception:
                    ok=False
                if ok:
                    _verified_atoms+=len(pkt)
                    _packet_current=i+1
                    _phase="CHECKPOINT"
                    cp_path(job_id).write_text(json.dumps({"next_packet":i+1,"verified_atoms":_verified_atoms,"retries":_retry_count}),encoding="utf-8")
                    publish_heartbeat(force=True)
                    break
                attempt+=1; _retry_count+=1; _phase="RETRY"; publish_heartbeat(force=True)
                if attempt>2: raise RuntimeError(f"packet {i+1} failed checker")
    _phase="VERIFIED_DONE"; publish_heartbeat(force=True)
    return f"VERIFIED_DONE atoms={len(atoms)} packets={len(packets)} retries={_retry_count}"

def publish_result(job_id,status,output):
    out=RESULTS/f"{job_id}.result"; RESULTS.mkdir(parents=True,exist_ok=True)
    out.write_text(f"JOB_ID={job_id}\nWORKER={WORKER}\nFUNCTION=hotspot_hive_campaign\nSTATUS={status}\nOUTPUT={output}\n")
    run("git","add",str(out.relative_to(ROOT)))
    if run("git","diff","--cached","--quiet",check=False).returncode!=0:
        run("git","commit","-m",f"HOTSPOT result {job_id}")
        run("git","pull","--rebase","origin","main")
        git_push_resilient()

def process_jobs():
    global _busy_job,_job_started,_phase,_packet_current,_packet_total,_verified_atoms,_retry_count
    for path in sorted(JOBS.glob("*.job")):
        job=parse_job(path); job_id=job.get("JOB_ID",path.stem)
        if job.get("WORKER")!=WORKER or job.get("FUNCTION")!="hotspot_hive_campaign": continue
        if (RESULTS/f"{job_id}.result").exists(): continue
        _busy_job=job_id; _job_started=time.time(); _phase="STARTING"
        _packet_current=_packet_total=_verified_atoms=_retry_count=0
        publish_heartbeat(force=True)
        try:
            publish_result(job_id,"DONE",run_campaign(job_id))
        except Exception as exc:
            publish_result(job_id,"FAILED",str(exc).replace("\n"," ")[:500])
        finally:
            _busy_job=""; _job_started=0.0; _phase=""; _packet_current=_packet_total=_verified_atoms=_retry_count=0
            publish_heartbeat(force=True)

print("ANDERSON HOUSE — HOTSPOT MINI-HIVE")
print("Workers: 2 (light duty)")
while True:
    try:
        pull(); process_bus(WORKER, ROOT); publish_heartbeat(); process_jobs()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"MAILBOX RETRY: {exc}",flush=True)
    time.sleep(INTERVAL)
