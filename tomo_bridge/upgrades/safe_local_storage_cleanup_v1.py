#!/usr/bin/env python3
import json, os, shutil, subprocess
from pathlib import Path

HOME = Path.home()
PREFIX = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"))

def du(path):
    try:
        p = subprocess.run(["du","-sk",str(path)], text=True, capture_output=True, timeout=60)
        if p.returncode == 0 and p.stdout.strip():
            return int(p.stdout.split()[0]) * 1024
    except Exception:
        pass
    return 0

def fmt(n):
    units=["B","KB","MB","GB"]
    x=float(n)
    for u in units:
        if x < 1024 or u==units[-1]:
            return f"{x:.1f} {u}"
        x/=1024

report={"before":{}, "cleanup":{}, "after":{}, "largest_home_entries":[]}

st=shutil.disk_usage(HOME)
report["before"]={"total":st.total,"used":st.used,"free":st.free,"free_human":fmt(st.free)}

# Largest top-level home entries (read-only inventory)
entries=[]
for p in HOME.iterdir():
    try:
        entries.append((du(p), str(p)))
    except Exception:
        pass
entries.sort(reverse=True)
report["largest_home_entries"]=[{"path":p,"bytes":n,"human":fmt(n)} for n,p in entries[:20]]

# Safe disposable targets only.
targets = [
    HOME / ".npm" / "_logs",
    HOME / ".cache" / "npm",
    HOME / ".cache" / "node-gyp",
    PREFIX / "var" / "cache" / "apt" / "archives",
]

for t in targets:
    before=du(t)
    removed=0
    if t.exists():
        try:
            if t.name=="archives":
                for child in t.iterdir():
                    if child.name=="partial":
                        continue
                    if child.is_file() and child.suffix==".deb":
                        removed += child.stat().st_size
                        child.unlink()
            else:
                for child in list(t.iterdir()):
                    try:
                        if child.is_dir() and not child.is_symlink():
                            removed += du(child)
                            shutil.rmtree(child)
                        else:
                            removed += child.stat().st_size
                            child.unlink()
                    except Exception:
                        pass
        except Exception as e:
            report["cleanup"][str(t)]={"before":before,"error":repr(e)}
            continue
    after=du(t)
    report["cleanup"][str(t)]={"before":before,"after":after,"reclaimed_estimate":max(0,before-after)}

# npm cache clean is safe; do not touch pnpm store because installed Codex may depend on it.
try:
    p=subprocess.run(["npm","cache","clean","--force"], text=True, capture_output=True, timeout=120)
    report["cleanup"]["npm_cache_clean"]={"returncode":p.returncode,"stdout":p.stdout[-2000:],"stderr":p.stderr[-2000:]}
except Exception as e:
    report["cleanup"]["npm_cache_clean"]={"error":repr(e)}

st=shutil.disk_usage(HOME)
report["after"]={"total":st.total,"used":st.used,"free":st.free,"free_human":fmt(st.free),
                 "reclaimed":st.free-report["before"]["free"],"reclaimed_human":fmt(max(0,st.free-report["before"]["free"]))}

print(json.dumps(report, indent=2))
