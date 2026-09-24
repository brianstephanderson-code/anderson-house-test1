#!/usr/bin/env python3
import re
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from hive_peer_bus import process_bus

ROOT = Path.home() / "anderson-house-mailbox"
JOBS = ROOT / "jobs"
RESULTS = ROOT / "results"
HEARTBEAT = ROOT / "hive" / "heartbeat" / "s20.txt"
INTERVAL = 30
HEARTBEAT_INTERVAL = 300
_last_heartbeat = 0.0
_busy_job = ""
_busy_function = ""
_job_started_at = 0.0
_phase = ""
_workers_active = 0
_batch_current = 0
_batch_total = 0
_progress_pct = 0.0
_verified_atoms = 0
_retry_count = 0
_checkpoint_packet = 0

def run(*args, check=True):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)

def pull():
    run("git", "pull", "--rebase", "--autostash", "origin", "main")


def git_push_resilient(max_attempts=4):
    """Push local commits while tolerating other hives advancing origin/main."""
    last = ""
    for attempt in range(1, max_attempts + 1):
        p = run("git", "push", "origin", "main", check=False)
        if p.returncode == 0:
            return
        last = (p.stderr or p.stdout or "").strip()
        # Another hive may have advanced main. Rebase our local commit and retry.
        run("git", "fetch", "origin")
        r = run("git", "rebase", "origin/main", check=False)
        if r.returncode != 0:
            # Leave no half-rebase behind; next mailbox loop can retry cleanly.
            run("git", "rebase", "--abort", check=False)
            raise RuntimeError(f"git rebase failed during push retry: {(r.stderr or r.stdout).strip()}")
        time.sleep(min(attempt, 3))
    raise RuntimeError(f"git push failed after {max_attempts} attempts: {last}")


def parse_job(path):
    data = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data

def read_text(path, default="NA"):
    try:
        return Path(path).read_text().strip()
    except Exception:
        return default

def battery():
    cap = read_text("/sys/class/power_supply/battery/capacity")
    status = read_text("/sys/class/power_supply/battery/status")
    return f"S20 battery: {cap}% — {status}"

def text_batch():
    # Light deterministic production work for the S20.
    # Reads a small local corpus if present, otherwise uses a built-in sample.
    candidates = [
        Path.home() / "tale.txt",
        ROOT / "README.md",
    ]
    text = ""
    for p in candidates:
        try:
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="replace")
                break
        except Exception:
            pass
    if not text:
        text = "Anderson House worker production sample. " * 5000

    lines = text.splitlines() or [text]
    words = text.split()
    sentences = [x for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
    digest = __import__("hashlib").sha256(text.encode("utf-8", "replace")).hexdigest()
    return (
        f"lines={len(lines)} words={len(words)} sentences={len(sentences)} "
        f"sha256={digest}"
    )

def cpu_pct():
    # First try Android/Termux 'top' for a one-shot system CPU sample.
    try:
        p = subprocess.run(
            ["top", "-b", "-n", "1"],
            text=True, capture_output=True, timeout=5
        )
        if p.returncode == 0:
            text = p.stdout
            m = re.search(r"(?:CPU usage|Cpu\(s\)|CPU):?\s*([^\n]+)", text, re.I)
            if m:
                line = m.group(1)
                idle = re.search(r"([0-9.]+)\s*%?\s*(?:idle|id)", line, re.I)
                if idle:
                    return f"{max(0.0,100.0-float(idle.group(1))):.1f}"
                nums = [float(x) for x in re.findall(r"([0-9.]+)%", line)]
                if nums:
                    return f"{min(sum(nums),100.0):.1f}"
    except Exception:
        pass

    # Fallback: sample /proc/stat if Android exposes it to Termux.
    def snap():
        parts = Path("/proc/stat").read_text().splitlines()[0].split()[1:]
        vals = [int(x) for x in parts]
        idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
        return sum(vals), idle
    try:
        t1, i1 = snap()
        time.sleep(0.5)
        t2, i2 = snap()
        dt = t2 - t1
        return f"{(100.0 * (dt - (i2 - i1)) / dt):.1f}" if dt > 0 else "NA"
    except Exception:
        return "NA"

def memory_pct():
    try:
        vals = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            if ":" in line:
                k,v = line.split(":",1)
                vals[k] = int(v.strip().split()[0])
        total = vals["MemTotal"]
        avail = vals.get("MemAvailable", vals.get("MemFree",0))
        return f"{100.0*(total-avail)/total:.1f}"
    except Exception:
        return "NA"

def temp_c():
    candidates = [
        "/sys/class/power_supply/battery/temp",
        "/sys/class/thermal/thermal_zone0/temp",
    ]
    for p in candidates:
        try:
            raw = float(Path(p).read_text().strip())
            if raw > 1000:
                raw /= 1000.0
            elif raw > 100:
                raw /= 10.0
            if -20 <= raw <= 120:
                return f"{raw:.1f}"
        except Exception:
            pass
    return "NA"

def health_snapshot():
    cap = read_text("/sys/class/power_supply/battery/capacity")
    charging = read_text("/sys/class/power_supply/battery/status")
    try:
        _,_,free = shutil.disk_usage(str(Path.home()))
        disk = f"{free/(1024**3):.1f}"
    except Exception:
        disk = "NA"
    uptime = "NA"
    try:
        raw = Path("/proc/uptime").read_text().split()[0]
        uptime = f"{float(raw)/3600:.1f}"
    except Exception:
        try:
            p = subprocess.run(["uptime", "-s"], text=True, capture_output=True, timeout=5)
            if p.returncode == 0 and p.stdout.strip():
                from datetime import datetime
                started = datetime.strptime(p.stdout.strip(), "%Y-%m-%d %H:%M:%S")
                uptime = f"{(datetime.now()-started).total_seconds()/3600:.1f}"
        except Exception:
            try:
                p = subprocess.run(["cat", "/proc/uptime"], text=True, capture_output=True, timeout=5)
                if p.returncode == 0 and p.stdout.strip():
                    uptime = f"{float(p.stdout.split()[0])/3600:.1f}"
            except Exception:
                pass
    return {
        "BATTERY_PCT": cap,
        "CHARGE_STATE": charging,
        "TEMP_C": temp_c(),
        "CPU_PCT": cpu_pct(),
        "MEMORY_PCT": memory_pct(),
        "DISK_FREE_GB": disk,
        "UPTIME_HOURS": uptime,
    }

def publish_heartbeat(force=False):
    global _last_heartbeat
    now = time.time()
    if not force and now - _last_heartbeat < HEARTBEAT_INTERVAL:
        return
    h = health_snapshot()
    state = "BUSY" if _busy_job else "FREE"
    elapsed_s = max(int(now - _job_started_at), 0) if _busy_job and _job_started_at else 0
    eta_s = 0
    if _busy_job and _progress_pct > 0:
        eta_s = max(int(elapsed_s * (100.0 - _progress_pct) / _progress_pct), 0)
    stamp = datetime.now(timezone.utc).isoformat()
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(
        f"WORKER=S20\nSTATUS=ALIVE\nSTATE={state}\n"
        f"JOB_ID={_busy_job}\nFUNCTION={_busy_function}\n"
        f"PHASE={_phase}\nWORKERS_ACTIVE={_workers_active}\n"
        f"BATCH_CURRENT={_batch_current}\nBATCH_TOTAL={_batch_total}\n"
        f"VERIFIED_ATOMS={_verified_atoms}\nRETRY_COUNT={_retry_count}\n"
        f"CHECKPOINT_PACKET={_checkpoint_packet}\n"
        f"PROGRESS_PCT={_progress_pct:.1f}\n"
        f"ELAPSED_SECONDS={elapsed_s}\nETA_SECONDS={eta_s}\n"
        f"BATTERY_PCT={h['BATTERY_PCT']}\nCHARGE_STATE={h['CHARGE_STATE']}\n"
        f"CPU_PCT={h['CPU_PCT']}\nMEMORY_PCT={h['MEMORY_PCT']}\n"
        f"DISK_FREE_GB={h['DISK_FREE_GB']}\nUPTIME_HOURS={h['UPTIME_HOURS']}\n"
        f"TEMP_C={h['TEMP_C']}\nUTC={stamp}\n",
        encoding="utf-8"
    )
    run("git", "add", str(HEARTBEAT.relative_to(ROOT)))
    changed = run("git", "diff", "--cached", "--quiet", check=False)
    if changed.returncode != 0:
        run("git", "commit", "-m", f"S20 heartbeat {stamp}")
        run("git", "pull", "--rebase", "origin", "main")
        git_push_resilient()
    _last_heartbeat = now

def repo_policy_scan():
    files = sorted((ROOT / "hive").rglob("*.md")) if (ROOT / "hive").exists() else []
    hard = unknown = headings = todos = lines_total = 0
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        lines_total += len(lines)
        hard += sum(1 for line in lines if re.search(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b", line, re.I))
        unknown += sum(1 for line in lines if re.search(r"\bUNKNOWN\b", line, re.I))
        headings += sum(1 for line in lines if re.match(r"^#{1,6}\s+", line))
        todos += sum(1 for line in lines if re.search(r"\b(TODO|TBD|FIXME)\b|\?\?\?", line, re.I))
    return f"files={len(files)} lines={lines_total} hard_rules={hard} unknown={unknown} headings={headings} todos={todos}"

def mailbox_gap_scan():
    jobs = {p.stem for p in JOBS.glob("*.job")}
    results = {p.name[:-7] for p in RESULTS.glob("*.result")}
    missing = sorted(jobs - results)
    orphan = sorted(results - jobs)
    return f"jobs_without_results={len(missing)} results_without_jobs={len(orphan)} sample_missing={','.join(missing[:20])}"

def repo_integrity_scan():
    import hashlib
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts)
    h = hashlib.sha256()
    total_bytes = 0
    for p in files:
        try:
            data = p.read_bytes()
            total_bytes += len(data)
            h.update(str(p.relative_to(ROOT)).encode())
            h.update(data)
        except Exception:
            pass
    return f"files={len(files)} bytes={total_bytes} sha256={h.hexdigest()}"

def _parallel_lane(payload):
    import hashlib, re
    docs, rounds = payload
    hard = unknown = headings = todos = 0
    h = hashlib.sha256()
    for _ in range(rounds):
        for path, text in docs:
            h.update(path.encode())
            h.update(text.encode("utf-8", "replace"))
            lines = text.splitlines()
            hard += sum(1 for line in lines if re.search(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b", line, re.I))
            unknown += sum(1 for line in lines if re.search(r"\bUNKNOWN\b", line, re.I))
            headings += sum(1 for line in lines if re.match(r"^#{1,6}\s+", line))
            todos += sum(1 for line in lines if re.search(r"\b(TODO|TBD|FIXME)\b|\?\?\?", line, re.I))
    return hard, unknown, headings, todos, h.hexdigest()

def _load_policy_docs():
    files = sorted((ROOT / "hive").rglob("*.md")) if (ROOT / "hive").exists() else []
    return [(str(p.relative_to(ROOT)), p.read_text(encoding="utf-8", errors="replace")) for p in files]

def four_worker_two_hour_test():
    global _phase, _workers_active, _batch_current, _batch_total, _progress_pct
    global _verified_atoms, _retry_count, _checkpoint_packet
    from concurrent.futures import ProcessPoolExecutor
    docs = _load_policy_docs()
    if not docs:
        return "FAILED no policy docs"

    log = ROOT / "results" / "s20_four_worker_metrics.csv"
    new_file = not log.exists()
    fh = log.open("a", encoding="utf-8")
    if new_file:
        fh.write("utc,phase,workers,batches,battery_pct,temp_c,cpu_pct,memory_pct,elapsed_s\n")

    def sample(phase, workers, batches, started, force_pulse=False):
        h = health_snapshot()
        fh.write(
            f"{datetime.now(timezone.utc).isoformat()},{phase},{workers},{batches},"
            f"{h['BATTERY_PCT']},{h['TEMP_C']},{h['CPU_PCT']},{h['MEMORY_PCT']},"
            f"{int(time.time()-started)}\n"
        )
        fh.flush()
        publish_heartbeat(force=force_pulse)

    # 5-minute 1-worker baseline.
    _phase = "BASELINE_1_WORKER"
    _workers_active = 1
    _batch_current = 0
    _batch_total = 0
    _progress_pct = 0.0
    baseline_started = time.time()
    baseline_batches = 0
    last_pulse = 0.0
    publish_heartbeat(force=True)
    while time.time() - baseline_started < 300:
        _parallel_lane((docs, 25))
        baseline_batches += 1
        _batch_current = baseline_batches
        _progress_pct = min(5.0 * (time.time() - baseline_started) / 300.0, 5.0)
        if time.time() - last_pulse >= HEARTBEAT_INTERVAL:
            sample("baseline", 1, baseline_batches, baseline_started, force_pulse=True)
            last_pulse = time.time()

    # Main 4-worker run for about two hours.
    _phase = "FOUR_WORKER"
    _workers_active = 4
    _batch_current = 0
    _batch_total = 0
    _progress_pct = 5.0
    run_started = time.time()
    batches = 0
    last_pulse = 0.0
    publish_heartbeat(force=True)
    with ProcessPoolExecutor(max_workers=4) as pool:
        while time.time() - run_started < 7200:
            list(pool.map(_parallel_lane, [(docs, 25)] * 4))
            batches += 1
            _batch_current = batches
            _progress_pct = min(5.0 + 95.0 * (time.time() - run_started) / 7200.0, 100.0)
            if time.time() - last_pulse >= HEARTBEAT_INTERVAL:
                sample("four_worker", 4, batches, run_started, force_pulse=True)
                last_pulse = time.time()

    _phase = "FOUR_WORKER_DONE"
    _workers_active = 0
    _batch_current = batches
    _progress_pct = 100.0
    sample("four_worker_done", 4, batches, run_started, force_pulse=True)
    fh.close()

    return (
        f"baseline_batches_5min={baseline_batches} "
        f"four_worker_batches_2h={batches} "
        f"metrics={log}"
    )

CHECKPOINTS = ROOT / "work" / "checkpoints"

def _shred_policy_atoms(lines_per_atom=40):
    """SHREDDER: deterministic STATE->ACTION->DONE atoms from policy markdown."""
    atoms = []
    atom_id = 0
    for path, text in _load_policy_docs():
        lines = text.splitlines()
        for start in range(0, len(lines), lines_per_atom):
            atom_id += 1
            chunk = "\n".join(lines[start:start + lines_per_atom])
            atoms.append({
                "id": atom_id,
                "source": path,
                "start_line": start + 1,
                "text": chunk,
            })
    return atoms

def _hive_atom_work(atom):
    import hashlib, re
    text = atom["text"]
    lines = text.splitlines()
    return {
        "id": atom["id"],
        "source": atom["source"],
        "start_line": atom["start_line"],
        "lines": len(lines),
        "hard_rules": sum(1 for line in lines if re.search(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b", line, re.I)),
        "unknown": sum(1 for line in lines if re.search(r"\bUNKNOWN\b", line, re.I)),
        "headings": sum(1 for line in lines if re.match(r"^#{1,6}\s+", line)),
        "todos": sum(1 for line in lines if re.search(r"\b(TODO|TBD|FIXME)\b|\?\?\?", line, re.I)),
        "sha256": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest(),
    }

def _hive_packet_worker(packet):
    return [_hive_atom_work(atom) for atom in packet]

def _check_packet(packet, result):
    """CHECKER: independently verify identity, completeness and content hash."""
    import hashlib
    if not isinstance(result, list) or len(result) != len(packet):
        return False, "count_mismatch"
    expected = {a["id"]: a for a in packet}
    seen = set()
    for row in result:
        atom_id = row.get("id")
        if atom_id not in expected or atom_id in seen:
            return False, "identity_mismatch"
        seen.add(atom_id)
        atom = expected[atom_id]
        digest = hashlib.sha256(atom["text"].encode("utf-8", "replace")).hexdigest()
        if row.get("sha256") != digest:
            return False, f"hash_mismatch_atom_{atom_id}"
        if row.get("lines") != len(atom["text"].splitlines()):
            return False, f"line_count_mismatch_atom_{atom_id}"
    return True, "VERIFIED"

def _checkpoint_path(job_id):
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", job_id or "s20-hive")
    return CHECKPOINTS / f"{safe}.json"

def _load_checkpoint(job_id):
    p = _checkpoint_path(job_id)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_checkpoint(job_id, data):
    p = _checkpoint_path(job_id)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, sort_keys=True, indent=2), encoding="utf-8")
    tmp.replace(p)

def s20_hive_campaign():
    """Local S20 hive: SHREDDER -> 4 workers -> CHECKER -> CHECKPOINT -> RETRY."""
    global _phase, _workers_active, _batch_current, _batch_total, _progress_pct
    global _verified_atoms, _retry_count, _checkpoint_packet

    from concurrent.futures import ProcessPoolExecutor

    atoms = _shred_policy_atoms(lines_per_atom=40)
    if not atoms:
        return "FAILED no atoms"

    packet_size = 8
    packets = [atoms[i:i + packet_size] for i in range(0, len(atoms), packet_size)]
    total_packets = len(packets)
    cp = _load_checkpoint(_busy_job)
    next_packet = min(int(cp.get("next_packet", 0) or 0), total_packets)
    verified_atoms = int(cp.get("verified_atoms", 0) or 0)
    retries = int(cp.get("retries", 0) or 0)

    _phase = "SHREDDED"
    _workers_active = 4
    _batch_total = total_packets
    _batch_current = next_packet
    _verified_atoms = verified_atoms
    _retry_count = retries
    _checkpoint_packet = next_packet
    _progress_pct = 100.0 * next_packet / total_packets if total_packets else 100.0
    publish_heartbeat(force=True)

    totals = {"hard_rules": 0, "unknown": 0, "headings": 0, "todos": 0}
    max_retries = 2

    with ProcessPoolExecutor(max_workers=4) as pool:
        packet_index = next_packet
        while packet_index < total_packets:
            wave_indexes = list(range(packet_index, min(packet_index + 4, total_packets)))
            wave_packets = [packets[i] for i in wave_indexes]

            _phase = "WORK"
            futures = [pool.submit(_hive_packet_worker, pkt) for pkt in wave_packets]

            for idx, pkt, fut in zip(wave_indexes, wave_packets, futures):
                attempt = 0
                while True:
                    try:
                        result = fut.result()
                        _phase = "CHECK"
                        ok, reason = _check_packet(pkt, result)
                    except Exception as exc:
                        ok, reason = False, f"worker_exception:{exc}"

                    if ok:
                        for row in result:
                            totals["hard_rules"] += row["hard_rules"]
                            totals["unknown"] += row["unknown"]
                            totals["headings"] += row["headings"]
                            totals["todos"] += row["todos"]

                        verified_atoms += len(pkt)
                        completed_packet = idx + 1
                        _batch_current = completed_packet
                        _verified_atoms = verified_atoms
                        _checkpoint_packet = completed_packet
                        _progress_pct = 100.0 * completed_packet / total_packets

                        _phase = "CHECKPOINT"
                        _save_checkpoint(_busy_job, {
                            "job_id": _busy_job,
                            "next_packet": completed_packet,
                            "verified_atoms": verified_atoms,
                            "retries": retries,
                            "total_packets": total_packets,
                            "total_atoms": len(atoms),
                            "updated_utc": datetime.now(timezone.utc).isoformat(),
                        })
                        publish_heartbeat(force=True)
                        break

                    attempt += 1
                    retries += 1
                    _retry_count = retries
                    _phase = "RETRY"
                    publish_heartbeat(force=True)
                    if attempt > max_retries:
                        raise RuntimeError(f"packet {idx + 1} failed checker after {attempt} attempts: {reason}")
                    result = _hive_packet_worker(pkt)
                    class _Done:
                        def result(self_inner):
                            return result
                    fut = _Done()

            packet_index = wave_indexes[-1] + 1

    _phase = "VERIFIED_DONE"
    _workers_active = 0
    _batch_current = total_packets
    _checkpoint_packet = total_packets
    _verified_atoms = len(atoms)
    _progress_pct = 100.0
    publish_heartbeat(force=True)

    return (
        f"VERIFIED_DONE atoms={len(atoms)} packets={total_packets} "
        f"retries={retries} hard_rules={totals['hard_rules']} "
        f"unknown={totals['unknown']} headings={totals['headings']} todos={totals['todos']} "
        f"checkpoint={_checkpoint_path(_busy_job)}"
    )

FUNCTIONS = {
    "battery": battery,
    "text_batch": text_batch,
    "repo_policy_scan": repo_policy_scan,
    "mailbox_gap_scan": mailbox_gap_scan,
    "repo_integrity_scan": repo_integrity_scan,
    "four_worker_two_hour_test": four_worker_two_hour_test,
    "s20_hive_campaign": s20_hive_campaign,
}

def publish_result(job_id, function, status, output):
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"{job_id}.result"
    out.write_text(
        f"JOB_ID={job_id}\n"
        f"WORKER=S20\n"
        f"FUNCTION={function}\n"
        f"STATUS={status}\n"
        f"OUTPUT={output}\n"
    )
    run("git", "add", str(out.relative_to(ROOT)))
    changed = run("git", "diff", "--cached", "--quiet", check=False)
    if changed.returncode == 0:
        return
    run("git", "commit", "-m", f"S20 result {job_id}")
    run("git", "pull", "--rebase", "origin", "main")
    git_push_resilient()

def process_jobs():
    global _busy_job, _busy_function, _job_started_at
    global _phase, _workers_active, _batch_current, _batch_total, _progress_pct
    JOBS.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    for path in sorted(JOBS.glob("*.job")):
        job = parse_job(path)
        job_id = job.get("JOB_ID", path.stem)
        worker = job.get("WORKER", "")
        function = job.get("FUNCTION", "")
        if worker != "S20":
            continue
        if (RESULTS / f"{job_id}.result").exists():
            continue
        _busy_job, _busy_function = job_id, function
        _job_started_at = time.time()
        _phase = "STARTING"
        _workers_active = 0
        _batch_current = 0
        _batch_total = 0
        _progress_pct = 0.0
        _verified_atoms = 0
        _retry_count = 0
        _checkpoint_packet = 0
        publish_heartbeat(force=True)
        try:
            fn = FUNCTIONS[function]
            output = fn()
            publish_result(job_id, function, "DONE", output)
            print(f"DONE: {job_id} -> {output}", flush=True)
        except Exception as exc:
            publish_result(job_id, function or "UNKNOWN", "FAILED", str(exc).replace("\n", " "))
            print(f"FAILED: {job_id} -> {exc}", flush=True)
        finally:
            _busy_job, _busy_function = "", ""
            _job_started_at = 0.0
            _phase = ""
            _workers_active = 0
            _batch_current = 0
            _batch_total = 0
            _progress_pct = 0.0
            _verified_atoms = 0
            _retry_count = 0
            _checkpoint_packet = 0
            publish_heartbeat(force=True)

print("ANDERSON HOUSE — S20 MAILBOX")
print("Watching GitHub for jobs...", flush=True)

while True:
    try:
        pull()
        process_bus(WORKER, ROOT)
        publish_heartbeat()
        process_jobs()
    except Exception as exc:
        print(f"MAILBOX RETRY: {exc}", flush=True)
    time.sleep(INTERVAL)
