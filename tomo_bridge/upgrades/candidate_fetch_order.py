#!/usr/bin/env python3
"""Choose a lane-balanced fetch order without changing candidate scoring."""
from urllib.parse import urlsplit

LANE_ORDER = ("official_candidate", "end_user", "other")

def _host(row):
    return urlsplit(str(row.get("url") or "")).netloc.lower().split(":")[0]

def balanced_fetch_order(rows, fetch_budget=None, max_per_host=2):
    """Round-robin evidence lanes while preserving rank within each lane."""
    queues={lane:[] for lane in LANE_ORDER}
    for row in rows:
        lane=row.get("source_lane") or "other"
        queues.setdefault(lane,[]).append(row)
    out=[]; counts={}
    limit=len(rows) if fetch_budget is None else max(0,int(fetch_budget))
    while len(out)<limit and any(queues.values()):
        progressed=False
        for lane in LANE_ORDER:
            q=queues.get(lane,[])
            pick=None
            for i,row in enumerate(q):
                if counts.get(_host(row),0)<max_per_host:
                    pick=q.pop(i); break
            if pick is None:
                continue
            out.append(pick); counts[_host(pick)]=counts.get(_host(pick),0)+1
            progressed=True
            if len(out)>=limit: break
        if not progressed: break
    return out

if __name__=="__main__":
    rows=[
      {"url":"https://agency.gov.au/a","source_lane":"official_candidate","score":10},
      {"url":"https://agency.gov.au/b","source_lane":"official_candidate","score":9},
      {"url":"https://agency.gov.au/c","source_lane":"official_candidate","score":8},
      {"url":"https://reddit.com/r/x/1","source_lane":"end_user","score":7},
      {"url":"https://forum.example.org/t/2","source_lane":"end_user","score":6},
      {"url":"https://independent.org/a","source_lane":"other","score":5},
    ]
    top=balanced_fetch_order(rows,fetch_budget=4,max_per_host=2)
    assert [x["source_lane"] for x in top[:3]]==["official_candidate","end_user","other"], top
    assert sum(_host(x)=="agency.gov.au" for x in top)<=2, top
    assert top[0]["score"]==10
    assert top[3]["score"]==9
    print("PASS balanced_fetch_order",[(x["source_lane"],_host(x)) for x in top])
