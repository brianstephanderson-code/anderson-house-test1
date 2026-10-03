#!/usr/bin/env python3
from pathlib import Path
p=Path.home()/".tomo_private_events"/"events.jsonl"
if not p.exists():
    print("LOCAL_INLET_LOG_MISSING")
    raise SystemExit(2)
count=sum(1 for _ in p.open("rb"))
print("LOCAL_INLET_LINE_COUNT="+str(count))
print("LOCAL_INLET_OK" if count>0 else "LOCAL_INLET_EMPTY")
