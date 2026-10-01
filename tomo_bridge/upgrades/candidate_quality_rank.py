#!/usr/bin/env python3
"""Small lane-neutral candidate quality ranker. Standard library only.

Ranks evidence candidates using observable result quality without allowing an
'official' label to automatically outrank end-user or independent evidence.
Route/lane diversity remains a separate function.
"""
import re
from urllib.parse import urlsplit

WORD_RE = re.compile(r"[a-z0-9]{3,}", re.I)


def _terms(text):
    return set(x.casefold() for x in WORD_RE.findall(str(text or "")))


def quality_score(row, purpose=""):
    """Return a deterministic, provider-independent discovery quality score."""
    title = str(row.get("title") or "").strip()
    snippet = str(row.get("snippet") or "").strip()
    url = str(row.get("url") or "").strip()
    score = 0

    # Basic result completeness. These are discovery hints, not evidence proof.
    if title:
        score += 2
    if len(snippet) >= 40:
        score += 2
    if url.startswith("https://"):
        score += 1
    try:
        p = urlsplit(url)
        if p.netloc and p.path not in ("", "/"):
            score += 1
    except Exception:
        pass

    # Reward topical overlap with PURPOSE, capped so keyword stuffing cannot win.
    wanted = _terms(purpose)
    found = _terms(title + " " + snippet)
    score += min(3, len(wanted & found))
    return score


def rank_within_lane(rows, purpose=""):
    """Stable quality ranking intended to run separately inside each route lane."""
    decorated=[]
    for i, row in enumerate(rows):
        item=dict(row)
        item["quality_score"] = quality_score(item, purpose)
        decorated.append((item["quality_score"], i, item))
    decorated.sort(key=lambda x: (-x[0], x[1]))
    return [x[2] for x in decorated]


if __name__ == "__main__":
    rows=[
      {"url":"http://noise.example/","title":"Other"},
      {"url":"https://example.org/salmon/bait","title":"Australian salmon bait guide","snippet":"Beach anglers compare pilchards and lures for Australian salmon in May."},
      {"url":"https://example.net/x","title":"Australian salmon"},
    ]
    ranked=rank_within_lane(rows,"Australian salmon beach bait May")
    assert ranked[0]["url"].startswith("https://example.org/"), ranked
    assert ranked[0]["quality_score"] > ranked[-1]["quality_score"]
    # Evidence lane is deliberately irrelevant to score.
    a={"url":"https://x.org/a","title":"Same","snippet":"x"*50,"source_lane":"official_candidate"}
    b=dict(a,source_lane="end_user")
    assert quality_score(a,"x") == quality_score(b,"x")
    print("PASS candidate_quality_rank",[(x["url"],x["quality_score"]) for x in ranked])
