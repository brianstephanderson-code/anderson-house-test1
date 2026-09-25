#!/usr/bin/env python3
import base64
import json
import re
import subprocess
import time
import shutil
import ctypes
import sys
from pathlib import Path

REPO = "brianstephanderson-code/anderson-house-test1"
JOBS_API = f"repos/{REPO}/contents/jobs"
RESULTS_API = f"repos/{REPO}/contents/results"
WORKER = "CLASSICQUILL"
INTERVAL = 15
TIMEOUT = 120
HEARTBEAT_INTERVAL = 300
_last_heartbeat = 0
_busy_job = ""
_busy_function = ""
_atom_current = 0
_atom_total = 0
_packet_current = 0
_packet_total = 0
_job_started_at = 0.0

AH = Path(r"C:\AH")
INBOX = AH / "IN"
OUTBOX = AH / "OUT"
CHECKPOINTS = AH / "WORK" / "checkpoints"
JOB_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
ALLOWED = {"uppercase", "lowercase", "wordcount", "campaign", "policy_audit", "function_pack", "hive_campaign"}
CAMPAIGN_FUNCS = {"uppercase", "lowercase", "wordcount"}

def safe_text(value):
    return "" if value is None else str(value)

def gh(*args, check=True):
    try:
        return subprocess.run(["gh", *args], text=True, capture_output=True, check=check, timeout=30)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("GitHub call timed out; mailbox will retry") from exc

def gh_json(*args):
    p = gh(*args)
    return json.loads(p.stdout)

def parse_job(text):
    data = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data

def result_exists(job_id):
    p = gh("api", f"{RESULTS_API}/{job_id}.result", check=False)
    return p.returncode == 0

def publish_result(job_id, function, status, output):
    text = (
        f"JOB_ID={job_id}\n"
        f"WORKER={WORKER}\n"
        f"FUNCTION={function}\n"
        f"STATUS={status}\n"
        f"OUTPUT={output}\n"
    )
    encoded = base64.b64encode(text.encode()).decode()
    p = gh("api", "--method", "PUT", f"{RESULTS_API}/{job_id}.result",
           "-f", f"message={WORKER} result {job_id}",
           "-f", f"content={encoded}", check=False)
    if p.returncode != 0 and "already exists" not in (p.stderr + p.stdout).lower():
        raise RuntimeError((p.stderr or p.stdout).strip())

def fetch_job(name):
    item = gh_json("api", f"{JOBS_API}/{name}")
    raw = base64.b64decode(item["content"]).decode("utf-8")
    return parse_job(raw)

def list_jobs():
    listing = gh_json("api", JOBS_API)
    return sorted(item["name"] for item in listing
                  if item.get("type") == "file" and item.get("name", "").endswith(".job"))

def run_local(job_id, function, data):
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    in_path = INBOX / f"{job_id}.json"
    out_path = OUTBOX / f"{job_id}.done.txt"
    if out_path.exists():
        return out_path.read_text(encoding="utf-8", errors="replace").strip()
    tmp = in_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"function": function, "data": data}), encoding="utf-8")
    tmp.replace(in_path)
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        if out_path.exists():
            return out_path.read_text(encoding="utf-8", errors="replace").strip()
        time.sleep(1)
    raise TimeoutError("Local worker timed out")

def apply_campaign_function(function, data):
    if function == "uppercase":
        return str(data).upper()
    if function == "lowercase":
        return str(data).lower()
    if function == "wordcount":
        return str(len(str(data).split()))
    raise ValueError(f"Campaign function not allowed: {function}")

def checkpoint_path(job_id):
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    return CHECKPOINTS / f"{job_id}.json"

def load_checkpoint(job_id):
    path = checkpoint_path(job_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def save_checkpoint(job_id, cycle, current):
    path = checkpoint_path(job_id)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"cycle": cycle, "current": current}), encoding="utf-8")
    tmp.replace(path)

def clear_checkpoint(job_id):
    path = checkpoint_path(job_id)
    if path.exists():
        path.unlink()

def run_campaign(job):
    job_id = job.get("JOB_ID", "campaign")
    funcs = [x.strip() for x in job.get("STEPS", "uppercase,wordcount").split(",") if x.strip()]
    if not funcs or any(f not in CAMPAIGN_FUNCS for f in funcs):
        raise ValueError("Invalid campaign STEPS")
    current = job.get("DATA", "")
    checkpoint = load_checkpoint(job_id)
    resumed = False
    resume_cycle = 0
    if checkpoint:
        try:
            resume_cycle = max(int(checkpoint.get("cycle", 0)), 0)
            current = checkpoint.get("current", current)
            resumed = resume_cycle > 0
        except Exception:
            resume_cycle = 0
    max_hours = min(max(float(job.get("MAX_HOURS", "10")), 0.01), 16.0)
    max_cycles = min(max(int(job.get("MAX_CYCLES", "1000")), 1), 10000)
    sleep_seconds = min(max(float(job.get("SLEEP_SECONDS", "1")), 0.0), 60.0)
    stop_on_stable = job.get("STOP_ON_STABLE", "YES").upper() not in {"NO", "FALSE", "0"}
    started = time.time()
    deadline = started + max_hours * 3600
    cycle = resume_cycle
    last_trace = f"resumed_from={resume_cycle}" if resumed else ""
    packet_total = max(int(job.get("PACKET_TOTAL", "0") or 0), 0)
    pulse_every = max(int(job.get("PROGRESS_EVERY", "10") or 10), 1)
    while cycle < max_cycles and time.time() < deadline:
        cycle += 1
        packet_current = 0
        if packet_total > 0 and max_cycles > 0:
            packet_current = min(packet_total, ((cycle - 1) * packet_total // max_cycles) + 1)
        set_progress(cycle, max_cycles, packet_current, packet_total, force=False)
        if cycle == 1 or cycle % pulse_every == 0 or cycle == max_cycles:
            publish_heartbeat(force=True)
        before = current
        for f in funcs:
            current = apply_campaign_function(f, current)
            last_trace = f"cycle={cycle};function={f};output={str(current)[:120]}"
        save_checkpoint(job_id, cycle, current)
        if stop_on_stable and current == before:
            clear_checkpoint(job_id)
            return f"DONE_STABLE cycles={cycle} elapsed={round(time.time()-started,2)}s output={current} trace={last_trace}"
        if sleep_seconds:
            time.sleep(sleep_seconds)
    reason = "MAX_CYCLES" if cycle >= max_cycles else "MAX_HOURS"
    if cycle >= max_cycles:
        clear_checkpoint(job_id)
    return f"DONE_{reason} cycles={cycle} elapsed={round(time.time()-started,2)}s output={current} trace={last_trace}"

def sync_repo_worker(repo_path, local_path):
    item = gh_json("api", f"repos/{REPO}/contents/{repo_path}")
    raw = base64.b64decode(item["content"])
    target = Path(local_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_bytes(raw)
    tmp.replace(target)

def run_policy_audit():
    local_script = r"C:\\AH\\BIN\\audit.py"
    sync_repo_worker("workers/classicquill_policy_audit.py", local_script)
    p = subprocess.run([sys.executable, local_script], text=True, capture_output=True, timeout=7200)
    if p.returncode != 0:
        raise RuntimeError(safe_text(p.stderr or p.stdout)[:1000])
    output = safe_text(p.stdout).strip()
    if not output:
        report_path = Path(r"C:\\AH\\OUT\\classicquill_policy_audit_latest.txt")
        if report_path.exists():
            output = report_path.read_text(encoding="utf-8", errors="replace").strip()
    if not output:
        raise RuntimeError("Policy audit returned empty output and no report file")
    return output


def run_function_pack():
    local_script = r"C:\\AH\\BIN\\function_pack.py"
    sync_repo_worker("workers/classicquill_function_pack.py", local_script)
    p = subprocess.run(["python", local_script], text=True, capture_output=True, timeout=7200)
    if p.returncode != 0:
        raise RuntimeError(safe_text(p.stderr or p.stdout)[:1000])
    output = safe_text(p.stdout).strip()
    if not output:
        raise RuntimeError("Function pack returned empty output")
    return output

def run_hive_campaign():
    local_script = r"C:\\AH\\MAILROOM\\workers\\classicquill_hive.py"
    sync_repo_worker("workers/classicquill_hive.py", local_script)
    p = subprocess.run(["python", local_script], text=True, capture_output=True, timeout=7200)
    if p.returncode != 0:
        raise RuntimeError(safe_text(p.stderr or p.stdout)[:1000])
    output = safe_text(p.stdout).strip()
    if not output:
        report_path = Path(r"C:\\AH\\OUT\\classicquill_hive_latest.txt")
        if report_path.exists():
            output = report_path.read_text(encoding="utf-8", errors="replace").strip()
    if not output:
        raise RuntimeError("Hive campaign returned empty output")
    return output

def health_snapshot():
    data = {"CPU_PCT":"NA","MEMORY_PCT":"NA","DISK_FREE_GB":"NA","UPTIME_HOURS":"NA","TEMP_C":"NA"}
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
                      ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
                      ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
                      ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
                      ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
        mem=MEMORYSTATUSEX(); mem.dwLength=ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
            data["MEMORY_PCT"]=str(int(mem.dwMemoryLoad))
    except Exception:
        pass
    try:
        _,_,free=shutil.disk_usage(str(AH))
        data["DISK_FREE_GB"]=f"{free/(1024**3):.1f}"
    except Exception:
        pass
    try:
        data["UPTIME_HOURS"]=f"{ctypes.windll.kernel32.GetTickCount64()/3600000:.1f}"
    except Exception:
        pass
    try:
        p=subprocess.run(["powershell","-NoProfile","-Command",
            "(Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval 1 -MaxSamples 1).CounterSamples.CookedValue"],
            text=True,capture_output=True,timeout=8)
        if p.returncode==0 and p.stdout.strip():
            data["CPU_PCT"]=f"{float(p.stdout.strip()):.1f}"
    except Exception:
        pass
    try:
        cmd=("$t=Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature "
             "-ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty CurrentTemperature; "
             "if($t){[math]::Round(($t/10)-273.15,1)}")
        p=subprocess.run(["powershell","-NoProfile","-Command",cmd],text=True,capture_output=True,timeout=8)
        if p.returncode==0 and p.stdout.strip():
            temp=float(p.stdout.strip())
            if -20 <= temp <= 120:
                data["TEMP_C"]=f"{temp:.1f}"
    except Exception:
        pass
    return data

def set_progress(atom_current=0, atom_total=0, packet_current=0, packet_total=0, force=False):
    global _atom_current, _atom_total, _packet_current, _packet_total
    _atom_current = max(int(atom_current or 0), 0)
    _atom_total = max(int(atom_total or 0), 0)
    _packet_current = max(int(packet_current or 0), 0)
    _packet_total = max(int(packet_total or 0), 0)
    if force:
        publish_heartbeat(force=True)

def publish_heartbeat(force=False):
    global _last_heartbeat
    now=time.time()
    if not force and now-_last_heartbeat < HEARTBEAT_INTERVAL:
        return
    from datetime import datetime, timezone
    stamp=datetime.now(timezone.utc).isoformat()
    state="BUSY" if _busy_job else "FREE"
    health=health_snapshot()
    elapsed_s = max(int(time.time() - _job_started_at), 0) if _busy_job and _job_started_at else 0
    avg_packet_s = 0
    eta_s = 0
    if _busy_job and _packet_current > 0:
        avg_packet_s = int(elapsed_s / _packet_current) if elapsed_s > 0 else 0
        remaining_packets = max(_packet_total - _packet_current, 0)
        eta_s = avg_packet_s * remaining_packets
    content=(f"WORKER={WORKER}\nSTATUS=ALIVE\nSTATE={state}\n"
             f"JOB_ID={_busy_job}\nFUNCTION={_busy_function}\n"
             f"ATOM_CURRENT={_atom_current}\nATOM_TOTAL={_atom_total}\n"
             f"PACKET_CURRENT={_packet_current}\nPACKET_TOTAL={_packet_total}\n"
             f"ELAPSED_SECONDS={elapsed_s}\nAVG_PACKET_SECONDS={avg_packet_s}\nETA_SECONDS={eta_s}\n"
             f"CPU_PCT={health['CPU_PCT']}\nMEMORY_PCT={health['MEMORY_PCT']}\n"
             f"DISK_FREE_GB={health['DISK_FREE_GB']}\nUPTIME_HOURS={health['UPTIME_HOURS']}\n"
             f"TEMP_C={health['TEMP_C']}\nUTC={stamp}\n")
    encoded=base64.b64encode(content.encode()).decode()
    path="hive/heartbeat/classicquill.txt"
    cur=gh("api", f"repos/{REPO}/contents/{path}", check=False)
    args=["api","--method","PUT",f"repos/{REPO}/contents/{path}",
          "-f",f"message={WORKER} heartbeat {stamp}",
          "-f",f"content={encoded}"]
    if cur.returncode==0:
        try:
            item=json.loads(cur.stdout)
            args += ["-f",f"sha={item['sha']}"]
        except Exception:
            pass
    p=gh(*args, check=False)
    if p.returncode==0:
        _last_heartbeat=now


def process_peer_bus_api():
    bus_messages = "hive/bus/messages"
    bus_acks = "hive/bus/acks"
    listing = gh("api", f"repos/{REPO}/contents/{bus_messages}", check=False)
    if listing.returncode != 0:
        return 0
    try:
        items = json.loads(listing.stdout)
    except Exception:
        return 0
    made = 0
    for item in items:
        if item.get("type") != "file" or not item.get("name", "").endswith(".msg"):
            continue
        raw = gh("api", f"repos/{REPO}/contents/{bus_messages}/{item['name']}", check=False)
        if raw.returncode != 0:
            continue
        try:
            obj = json.loads(raw.stdout)
            text = base64.b64decode(obj["content"]).decode("utf-8", "replace")
            msg = parse_job(text)
        except Exception:
            continue
        if msg.get("CHANNEL", "").upper() != "CROSSTALK":
            continue
        if msg.get("TO") not in {WORKER, "ALL"}:
            continue
        mid = msg.get("MESSAGE_ID", item["name"][:-4])
        ack_path = f"{bus_acks}/{mid}.{WORKER}.ack"
        if gh("api", f"repos/{REPO}/contents/{ack_path}", check=False).returncode == 0:
            continue
        typ = msg.get("TYPE", "").upper()
        payload = msg.get("PAYLOAD", "")
        dept = msg.get("DEPT", "GENERAL").upper()
        if typ == "PING":
            status, detail = "PONG", f"pong_from={WORKER};dept={dept}"
        elif typ == "STATUS_REQUEST":
            status, detail = "STATUS", f"alive={WORKER};dept={dept}"
        elif typ == "VERIFY_REQUEST":
            import hashlib
            status, detail = "VERIFIED", f"dept={dept};sha256={hashlib.sha256(payload.encode('utf-8','replace')).hexdigest()}"
        elif typ == "ACK":
            status, detail = "ACK_RECEIVED", "ack_not_replied"
        else:
            status, detail = "UNSUPPORTED", f"type={typ or 'UNKNOWN'}"
        from datetime import datetime, timezone
        stamp = datetime.now(timezone.utc).isoformat()
        ack_text = (
            f"MESSAGE_ID={mid}\nFROM={WORKER}\nTO={msg.get('FROM','')}\nTYPE=ACK\n"
            f"STATUS={status}\nDETAIL={detail}\nCORRELATION_ID={mid}\nUTC={stamp}\n"
        )
        encoded = base64.b64encode(ack_text.encode()).decode()
        put = gh("api", "--method", "PUT", f"repos/{REPO}/contents/{ack_path}",
                 "-f", f"message={WORKER} peer-bus ack {stamp}",
                 "-f", f"content={encoded}", check=False)
        if put.returncode == 0:
            made += 1
    return made

def process_once():
    process_peer_bus_api()
    publish_heartbeat()
    for name in list_jobs():
        job = fetch_job(name)
        job_id = job.get("JOB_ID", Path(name).stem)
        worker = job.get("WORKER", "")
        function = job.get("FUNCTION", "")
        data = job.get("DATA", "")
        if worker != WORKER:
            continue
        if not JOB_ID_RE.fullmatch(job_id):
            print(f"QUARANTINE: invalid job id in {name}", flush=True)
            continue
        if result_exists(job_id):
            continue
        if function not in ALLOWED:
            publish_result(job_id, function or "UNKNOWN", "FAILED", "Function not allowed")
            continue
        global _busy_job, _busy_function, _job_started_at
        _busy_job, _busy_function = job_id, function
        _job_started_at = time.time()
        atom_total = int(job.get("ATOM_TOTAL", "0") or 0)
        packet_total = int(job.get("PACKET_TOTAL", "0") or 0)
        set_progress(0, atom_total, 0, packet_total, force=False)
        publish_heartbeat(force=True)
        try:
            output = run_campaign(job) if function == "campaign" else (run_policy_audit() if function == "policy_audit" else (run_function_pack() if function == "function_pack" else (run_hive_campaign() if function == "hive_campaign" else run_local(job_id, function, data))))
            publish_result(job_id, function, "DONE", output)
            print(f"DONE: {job_id} -> {output}", flush=True)
        except Exception as exc:
            message = str(exc).replace("\n", " ")[:500]
            publish_result(job_id, function, "FAILED", message)
            print(f"FAILED: {job_id} -> {message}", flush=True)
        finally:
            _busy_job, _busy_function = "", ""
            _job_started_at = 0.0
            set_progress(0, 0, 0, 0, force=False)
            publish_heartbeat(force=True)

print("ANDERSON HOUSE — CLASSICQUILL MAILBOX")
print("Road: GitHub API <-> CLASSICQUILL")
print("Allowed functions: " + ", ".join(sorted(ALLOWED)), flush=True)
while True:
    try:
        process_once()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"MAILBOX RETRY: {str(exc).replace(chr(10), ' ')[:500]}", flush=True)
    time.sleep(INTERVAL)
