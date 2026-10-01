#!/usr/bin/env python3
"""Small reusable search/discovery quality functions. Standard library only."""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING_PREFIXES=("utm_","fbclid","gclid","mc_")
END_USER_HOST_HINTS=("reddit.com","stackexchange.com","stackoverflow.com","forums.","forum.","community.")
OFFICIAL_SUFFIXES=(".gov",".gov.au",".gov.uk",".edu",".edu.au")

def canonical_url(raw):
    """Remove fragments/common tracking noise without changing useful query parameters."""
    try:
        p=urlsplit(str(raw or "").strip())
        if not p.scheme or not p.netloc: return str(raw or "").strip()
        kept=[]
        for k,v in parse_qsl(p.query,keep_blank_values=True):
            lk=k.lower()
            if lk in ("fbclid","gclid") or any(lk.startswith(x) for x in ("utm_","mc_")): continue
            kept.append((k,v))
        path=p.path.rstrip("/") or "/"
        return urlunsplit((p.scheme.lower(),p.netloc.lower(),path,urlencode(kept),""))
    except Exception:
        return str(raw or "").strip()

def dedupe_candidates(rows):
    out=[]; seen=set()
    for row in rows:
        key=canonical_url(row.get("url"))
        if not key or key in seen: continue
        seen.add(key); item=dict(row); item["canonical_url"]=key; out.append(item)
    return out

def source_lane(row):
    """Coarse provenance lane used only to diversify reading order, never as proof of authority."""
    host=urlsplit(str(row.get("url") or "")).netloc.lower().split(":")[0]
    if any(host==h or host.endswith("."+h) for h in END_USER_HOST_HINTS if not h.endswith(".")) or any(x in host for x in ("forums.","forum.","community.")):
        return "end_user"
    if any(host.endswith(s) for s in OFFICIAL_SUFFIXES): return "official_candidate"
    return "other"

def diversify_ranked(rows,max_per_host=2):
    """Preserve ranking while preventing one host from occupying the whole fetch budget."""
    chosen=[]; deferred=[]; counts={}
    for row in rows:
        host=urlsplit(str(row.get("url") or "")).netloc.lower()
        if counts.get(host,0)<max_per_host:
            item=dict(row); item["source_lane"]=source_lane(item); chosen.append(item); counts[host]=counts.get(host,0)+1
        else: deferred.append(row)
    for row in deferred:
        item=dict(row); item["source_lane"]=source_lane(item); chosen.append(item)
    return chosen

if __name__=="__main__":
    sample=[
      {"url":"https://example.gov.au/page?utm_source=x","title":"official"},
      {"url":"https://example.gov.au/page","title":"duplicate"},
      {"url":"https://reddit.com/r/test/comments/1/x","title":"user"},
      {"url":"https://example.gov.au/second","title":"official2"},
      {"url":"https://example.gov.au/third","title":"official3"},
      {"url":"https://other.org/a","title":"other"},
    ]
    d=dedupe_candidates(sample); ranked=diversify_ranked(d,max_per_host=2)
    assert len(d)==5, d
    assert ranked[0]["source_lane"]=="official_candidate"
    assert any(x["source_lane"]=="end_user" for x in ranked)
    assert ranked[-1]["title"]=="official3", ranked
    print("PASS discovery_quality",[(x["title"],x["source_lane"]) for x in ranked])
