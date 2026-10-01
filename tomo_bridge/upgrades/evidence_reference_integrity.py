#!/data/data/com.termux/files/usr/bin/python
"""Small claim-to-source reference integrity check for 3 Amigos verification.

Run before evidence-lane classification. It detects claims that have no source
IDs, point at missing source records, or point at source records with no URL.
It does not fetch, classify, or promote anything.
"""


def evidence_reference_failures(claims, sources_by_id):
    """Return broken claim/source references without mutating inputs."""
    sources_by_id = sources_by_id or {}
    failures = []
    for index, claim in enumerate(claims or []):
        source_ids = [str(x) for x in (claim.get("source_ids") or [])]
        missing = [source_id for source_id in source_ids if source_id not in sources_by_id]
        empty_url = [
            source_id for source_id in source_ids
            if source_id in sources_by_id
            and not str((sources_by_id[source_id] or {}).get("url") or "").strip()
        ]
        if not source_ids or missing or empty_url:
            failures.append({
                "claim_index": index,
                "claim": str(claim.get("text") or "")[:120],
                "no_source_ids": not bool(source_ids),
                "missing_source_ids": missing,
                "empty_url_source_ids": empty_url,
            })
    return failures
