#!/usr/bin/env python3
"""Measure source-family concentration from a route batch record.

Measurement only. Diversity is not relevance, truth, sufficiency, or DONE.
"""

from collections import Counter
from typing import Iterable, Mapping


def family_concentration(items: Iterable[Mapping[str, object]], *, job_id: str,
                         route_id: str, batch_id: str) -> dict:
    """Measure family concentration among USEFUL evidence items only."""
    rows = list(items)
    useful = [r for r in rows if r.get("judgment") == "USEFUL"]
    families = []
    for i, r in enumerate(useful):
        family = r.get("source_family")
        if not isinstance(family, str) or not family.strip():
            raise ValueError(f"missing_source_family:{i}")
        families.append(family.strip())
    counts = Counter(families)
    total = len(families)
    dominant = max(counts.values(), default=0)
    return {
        "job_id": job_id,
        "route_id": route_id,
        "batch_id": batch_id,
        "useful_evidence_count": total,
        "families_seen": len(counts),
        "family_counts": dict(sorted(counts.items())),
        "dominant_family_share": (dominant / total) if total else None,
        "concentration_measured": bool(total),
    }
