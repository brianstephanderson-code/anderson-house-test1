#!/data/data/com.termux/files/usr/bin/python
"""Small per-claim evidence-lane check for 3 Amigos verification.

A run can contain both official and end-user sources while an individual claim
is supported by only one lane. This function detects that boundary without
changing search, provenance classification, or warehouse policy.
"""

def claim_lane_failures(claims, sources_by_id, required_classes, classify_source):
    """Return claims missing one or more required evidence classes."""
    required=set(required_classes or [])
    failures=[]
    if not required:
        return failures
    for index, claim in enumerate(claims or []):
        source_ids=[str(x) for x in (claim.get("source_ids") or [])]
        classes={
            classify_source(sources_by_id[source_id].get("url"))
            for source_id in source_ids
            if source_id in sources_by_id
        }
        missing=sorted(required-classes)
        if missing:
            failures.append({
                "claim_index":index,
                "claim":str(claim.get("text") or "")[:120],
                "missing_source_classes":missing,
            })
    return failures
