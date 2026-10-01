#!/usr/bin/env python3
"""Small deterministic cast planner for route-diverse discovery. Standard library only."""
import re

LANES = (
    ("broad", "{purpose}"),
    ("official", "{purpose} official guidance policy documentation"),
    ("end_user", "{purpose} forum reddit experience problems"),
    # Independent evidence is neither the publisher/authority nor the operator.
    # Keep it separate so corroboration can come from a third evidence door.
    ("independent", "{purpose} independent analysis review comparison evidence"),
    ("failure", "{purpose} failed problem issue limitation"),
)

def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()

def plan_casts(purpose, required_functions=(), max_casts=6):
    """Create distinct casts without binding discovery to any search provider."""
    purpose = clean(purpose)
    funcs = [clean(x) for x in required_functions if clean(x)]
    seed = clean(" ".join([purpose] + funcs))
    if not seed:
        return []
    out=[]; seen=set()
    for lane, template in LANES:
        q=clean(template.format(purpose=seed))
        key=q.casefold()
        if key not in seen:
            seen.add(key); out.append({"lane":lane,"query":q})
        if len(out)>=max_casts: return out
    # A function-first cast is deliberately separate from evidence-lane casts.
    if funcs and len(out)<max_casts:
        q=clean(f'{purpose} "' + '" "'.join(funcs) + '"')
        if q.casefold() not in seen:
            out.append({"lane":"function_first","query":q})
    return out[:max_casts]

if __name__ == "__main__":
    rows=plan_casts("catch Australian salmon WA May", ["beach fishing", "bait selection"])
    assert len(rows)==6, rows
    assert len({x["query"].casefold() for x in rows})==len(rows)
    assert {x["lane"] for x in rows} >= {"broad","official","end_user","independent","failure","function_first"}
    assert plan_casts("", []) == []
    # Small budgets remain deterministic and do not silently duplicate casts.
    short=plan_casts("salmon bait", [], max_casts=3)
    assert [x["lane"] for x in short] == ["broad","official","end_user"], short
    print("PASS cast_diversity", [(x["lane"],x["query"]) for x in rows])
