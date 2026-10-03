#!/usr/bin/env python3
import json, os, subprocess
from pathlib import Path

ROOT = Path.home() / "downloads"

def du_bytes(p: Path):
    try:
        r = subprocess.run(["du","-sk",str(p)], text=True, capture_output=True, timeout=90)
        if r.returncode == 0 and r.stdout.strip():
            return int(r.stdout.split()[0]) * 1024
    except Exception:
        pass
    return 0

def fmt(n):
    units=["B","KB","MB","GB","TB"]
    x=float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:.1f} {u}"
        x/=1024

def classify(p: Path):
    name=p.name.lower()
    # Clearly disposable/download residue patterns only; do not delete here.
    disposable_ext={".tmp",".part",".crdownload",".download",".log"}
    if p.suffix.lower() in disposable_ext:
        return "safe_candidate"
    if name in {"cache","tmp","temp"}:
        return "safe_candidate"
    if p.is_dir() and name in {"node_modules","__pycache__"}:
        return "safe_candidate"
    # Project-like/archive-like material needs GitHub verification first.
    if any(k in name for k in ["sleepy","three_amigos","anderson","webster","adelle","backup","production","kdp","hive","bridge"]):
        return "needs_github_check"
    return "review"

items=[]
if ROOT.exists():
    for p in ROOT.iterdir():
        try:
            n=du_bytes(p)
            items.append({
                "name": p.name,
                "path": str(p),
                "type": "dir" if p.is_dir() else "file",
                "bytes": n,
                "human": fmt(n),
                "classification": classify(p),
            })
        except Exception as e:
            items.append({"name":p.name,"path":str(p),"error":repr(e)})

items.sort(key=lambda x: x.get("bytes",0), reverse=True)

out={
    "root": str(ROOT),
    "total_bytes": sum(x.get("bytes",0) for x in items),
    "total_human": fmt(sum(x.get("bytes",0) for x in items)),
    "top_items": items[:100],
    "summary": {}
}
for x in items:
    c=x.get("classification","unknown")
    out["summary"].setdefault(c, {"count":0,"bytes":0})
    out["summary"][c]["count"] += 1
    out["summary"][c]["bytes"] += x.get("bytes",0)
for c,v in out["summary"].items():
    v["human"]=fmt(v["bytes"])

print(json.dumps(out, indent=2))
