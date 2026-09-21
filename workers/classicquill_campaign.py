#!/usr/bin/env python3
import time
from dataclasses import dataclass

ALLOWED = {"uppercase", "lowercase", "wordcount"}

@dataclass
class Campaign:
    campaign_id: str
    data: str
    functions: list[str]
    max_hours: float = 10.0
    max_cycles: int = 1000
    sleep_seconds: float = 0.25
    stop_on_stable: bool = True

def apply_function(function, data):
    if function == "uppercase":
        return str(data).upper()
    if function == "lowercase":
        return str(data).lower()
    if function == "wordcount":
        return str(len(str(data).split()))
    raise ValueError(f"Function not allowed: {function}")

def run_campaign(c):
    if not c.functions:
        raise ValueError("Campaign has no functions")
    for f in c.functions:
        if f not in ALLOWED:
            raise ValueError(f"Function not allowed: {f}")

    started = time.time()
    deadline = started + max(0.01, c.max_hours) * 3600
    current = c.data
    cycle = 0
    evidence = []

    while cycle < c.max_cycles and time.time() < deadline:
        cycle += 1
        before_cycle = current

        for function in c.functions:
            output = apply_function(function, current)
            evidence.append(
                f"CYCLE={cycle};FUNCTION={function};INPUT={current[:120]};OUTPUT={output[:120]}"
            )
            current = output

        if c.stop_on_stable and current == before_cycle:
            return {
                "status": "DONE_STABLE",
                "cycles": cycle,
                "output": current,
                "elapsed_seconds": round(time.time() - started, 2),
                "evidence": evidence,
            }

        if c.sleep_seconds:
            time.sleep(c.sleep_seconds)

    reason = "MAX_CYCLES" if cycle >= c.max_cycles else "MAX_HOURS"
    return {
        "status": f"DONE_{reason}",
        "cycles": cycle,
        "output": current,
        "elapsed_seconds": round(time.time() - started, 2),
        "evidence": evidence,
    }
